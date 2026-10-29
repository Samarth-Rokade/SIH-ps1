"""One-off pipeline: projects.csv + trained models -> populated SQLite DB.

    data/projects.csv
        -> feature engineering (ml/features.py, same code path as training)
        -> delay model (probability + months)
        -> cost model (overrun probability + predicted final cost)
        -> risk engine (weighted score + level)
        -> SHAP drivers
        -> alerts (rule-based from risk level + dominant driver)
        -> backend/paimana.db

Run from the project root:
    python -m backend.app.ml.seed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from ml.features import build_cost_features, build_delay_features  # noqa: E402

from app.database.database import Base, SessionLocal, engine  # noqa: E402
from app.database import models  # noqa: E402
from app.ml import risk_engine, shap_service  # noqa: E402
from app.utils.constants import DATA_AS_OF  # noqa: E402
from app.utils.state_coordinates import get_centroid  # noqa: E402

DATA_PATH = ROOT / "data" / "projects.csv"
MODEL_DIR = ROOT / "ml" / "models"
RNG = np.random.default_rng(42)
JITTER_DEGREES = 0.35

ALERT_RULES = {
    "Progress Gap": ("progress_stagnation", "Project progress has significantly slowed."),
    "Physical Progress": ("progress_stagnation", "Physical progress remains well below expectations for this stage."),
    "Time Elapsed vs Plan": ("schedule_overrun", "Project has consumed significantly more time than its planned duration."),
    "Expenditure Utilization": ("expenditure_divergence", "Expenditure is diverging from the planned trajectory."),
    "Expenditure vs Revised Cost": ("expenditure_divergence", "Expenditure is diverging from the planned trajectory."),
    "Milestone Slippage": ("milestone_risk", "Upcoming milestones have a high failure probability."),
    "Monthly Spending Rate": ("expenditure_divergence", "Spending rate is inconsistent with progress."),
    "Historical Schedule Slippage": ("milestone_risk", "Prior schedule slippage raises risk of further delay."),
}
DEFAULT_ALERT = ("general_risk", "Project risk indicators require review.")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=[
            "approval_date",
            "start_date",
            "planned_completion",
            "revised_completion",
            "actual_completion",
        ],
    )
    # A handful of data_quality_flag=1 rows have a corrupt start_date (1900-01-01)
    # that leaves progress_gap_pct/time_elapsed_pct undefined (division by a
    # ~0-month planned duration). Neutralize rather than drop, so those
    # projects are still displayed - the quality flag marks them as unreliable.
    df["progress_gap_pct"] = df["progress_gap_pct"].fillna(0)
    df["time_elapsed_pct"] = df["time_elapsed_pct"].fillna(0)
    return df


def jittered_coordinates(states: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    lats, lons = [], []
    for state in states:
        lat, lon = get_centroid(state)
        lats.append(lat + RNG.uniform(-JITTER_DEGREES, JITTER_DEGREES))
        lons.append(lon + RNG.uniform(-JITTER_DEGREES, JITTER_DEGREES))
    return np.array(lats), np.array(lons)


def trend_from_progress_gap(gap_pct: float) -> str:
    if gap_pct < -5:
        return "increasing"
    if gap_pct > 5:
        return "decreasing"
    return "stable"


def build_alert(project_id: str, seq: int, risk_score: float, risk_level: str, drivers: list[dict]) -> models.Alert | None:
    if risk_level not in ("critical", "high", "medium"):
        return None
    top_feature = drivers[0]["feature"] if drivers else None
    alert_type, message = ALERT_RULES.get(top_feature, DEFAULT_ALERT)
    offset = {"critical": RNG.uniform(8, 18), "high": RNG.uniform(5, 12), "medium": RNG.uniform(2, 8)}[risk_level]
    risk_before = max(0.0, risk_score - offset)
    return models.Alert(
        alert_id=f"A{1000 + seq}",
        project_id=project_id,
        severity=risk_level,
        alert_type=alert_type,
        title=message,
        message=message,
        detected_at=DATA_AS_OF,
        status="new",
        risk_before=round(risk_before, 1),
        risk_current=round(risk_score, 1),
    )


def main() -> None:
    print("Loading data + models...")
    df = load_data()
    delay_artifact = joblib.load(MODEL_DIR / "delay_model.pkl")
    cost_artifact = joblib.load(MODEL_DIR / "cost_model.pkl")

    X_delay = build_delay_features(df, delay_artifact["categories"])
    X_cost = build_cost_features(df, cost_artifact["categories"])

    delay_prob = delay_artifact["classifier"].predict_proba(X_delay)[:, 1]
    delay_months_pred = np.clip(delay_artifact["regressor"].predict(X_delay), 0, None)
    residual_std = delay_artifact["residual_std"]
    delay_lower = np.clip(np.round(delay_months_pred - residual_std), 0, None)
    delay_upper = np.round(delay_months_pred + residual_std)

    cost_overrun_prob = cost_artifact["classifier"].predict_proba(X_cost)[:, 1]
    escalation_pred_pct = cost_artifact["regressor"].predict(X_cost)
    # current_cost (revised_cost) is an already-realized, official figure, so the
    # model's forecast represents further risk *beyond* it and should never
    # undercut it - floor the forecast there rather than showing a negative
    # "additional exposure".
    modeled_final_cost = df["original_cost"] * (1 + escalation_pred_pct / 100)
    predicted_final_cost = modeled_final_cost.clip(lower=df["revised_cost"])
    additional_exposure = predicted_final_cost - df["revised_cost"]
    # Recompute the displayed escalation % from the (possibly floored) forecast
    # so original/current/predicted/escalation stay mutually consistent.
    escalation_display_pct = (predicted_final_cost - df["original_cost"]) / df["original_cost"] * 100

    progress_risk = (-df["progress_gap_pct"]).clip(0, 100)
    mismatch = (df["physical_progress"] - df["expenditure_pct_of_revised_cost"]).abs()
    financial_risk = (mismatch * risk_engine.FINANCIAL_RISK_SCALE).clip(0, 100)
    score = (
        risk_engine.DELAY_WEIGHT * delay_prob * 100
        + risk_engine.COST_WEIGHT * cost_overrun_prob * 100
        + risk_engine.PROGRESS_WEIGHT * progress_risk
        + risk_engine.FINANCIAL_WEIGHT * financial_risk
    ).clip(0, 100)
    levels = score.apply(risk_engine.risk_level) if hasattr(score, "apply") else pd.Series(score).apply(risk_engine.risk_level)

    print("Computing SHAP risk drivers (this can take a minute)...")
    drivers_per_row = shap_service.compute_all_drivers(
        delay_artifact["classifier"], X_delay, score.to_numpy()
    )

    lats, lons = jittered_coordinates(df["state"])

    print("Rebuilding database...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()

    alert_seq = 0
    for i, row in df.iterrows():
        revised_completion = row["revised_completion"]
        current_completion = (
            revised_completion.date() if pd.notna(revised_completion) else row["planned_completion"].date()
        )

        project = models.Project(
            project_id=row["project_id"],
            project_name=row["project_name"],
            ministry=row["ministry"],
            sector=row["sector"],
            state=row["state"],
            original_cost_crore=float(row["original_cost"]),
            current_cost_crore=float(row["revised_cost"]),
            expenditure_crore=float(row["expenditure"]),
            physical_progress=float(row["physical_progress"]),
            start_date=row["start_date"].date(),
            original_completion_date=row["planned_completion"].date(),
            current_completion_date=current_completion,
            actual_completion_date=row["actual_completion"].date() if pd.notna(row["actual_completion"]) else None,
            status=row["status"],
            data_source=row["data_source"],
            data_quality_flag=int(row["data_quality_flag"]),
            latitude=float(lats[i]),
            longitude=float(lons[i]),
            progress_gap_pct=float(row["progress_gap_pct"]),
            time_elapsed_pct=float(row["time_elapsed_pct"]),
            expenditure_pct_of_revised_cost=float(row["expenditure_pct_of_revised_cost"]),
            project_age_months=int(row["project_age_months"]),
        )

        drivers = drivers_per_row[i]
        prediction = models.ProjectPrediction(
            project_id=row["project_id"],
            delay_probability=round(float(delay_prob[i]), 4),
            predicted_delay_months=int(round(delay_months_pred[i])),
            delay_range_lower=int(delay_lower[i]),
            delay_range_upper=int(delay_upper[i]),
            cost_overrun_probability=round(float(cost_overrun_prob[i]), 4),
            predicted_final_cost_crore=round(float(predicted_final_cost.iloc[i]), 2),
            expected_escalation_pct=round(float(escalation_display_pct.iloc[i]), 2),
            additional_exposure_crore=round(float(additional_exposure.iloc[i]), 2),
            risk_score=round(float(score.iloc[i]), 1),
            risk_level=levels.iloc[i],
            progress_risk=round(float(progress_risk.iloc[i]), 1),
            financial_risk=round(float(financial_risk.iloc[i]), 1),
            confidence=risk_engine.confidence_from_probability(float(delay_prob[i])),
            trend=trend_from_progress_gap(float(row["progress_gap_pct"])),
            drivers_json=json.dumps(drivers),
        )
        project.prediction = prediction
        session.add(project)

        alert = build_alert(row["project_id"], alert_seq, float(score.iloc[i]), levels.iloc[i], drivers)
        if alert is not None:
            alert_seq += 1
            session.add(alert)

    session.commit()

    total = len(df)
    dist = levels.value_counts().to_dict()
    print(f"Seeded {total} projects.")
    print(f"Risk distribution: {dist}")
    print(f"Alerts generated: {alert_seq}")
    session.close()


if __name__ == "__main__":
    main()
