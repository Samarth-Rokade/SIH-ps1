"""Serving-time model access: the same feature pipeline and scoring formulas as
backend/app/ml/seed.py, usable on a single (possibly what-if modified) project.

Models and the source projects.csv are loaded lazily once and cached, so the
FastAPI process pays the load cost only when the simulator or system endpoints
are first used.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.features import build_cost_features, build_delay_features  # noqa: E402

from app.ml import risk_engine  # noqa: E402

DATA_PATH = ROOT / "data" / "projects.csv"
MODEL_DIR = ROOT / "ml" / "models"

# Milestone recovery is a scenario lever, not something the models were trained
# on: it is modeled as the share of accumulated schedule slippage that an
# intervention wins back (fed into the cost model's slippage features) and the
# same share trimmed off the predicted delay.
RECOVERY_FACTORS = {"none": 0.0, "low": 0.10, "medium": 0.25, "high": 0.40}


@dataclass(frozen=True)
class Prediction:
    delay_probability: float
    predicted_delay_months: int
    cost_overrun_probability: float
    predicted_final_cost_crore: float
    risk_score: float
    risk_level: str


@lru_cache(maxsize=1)
def delay_artifact() -> dict:
    return joblib.load(MODEL_DIR / "delay_model.pkl")


@lru_cache(maxsize=1)
def cost_artifact() -> dict:
    return joblib.load(MODEL_DIR / "cost_model.pkl")


@lru_cache(maxsize=1)
def projects_frame() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["approval_date", "start_date", "planned_completion", "revised_completion", "actual_completion"],
    )
    # Same neutralization as seed.load_data() for the few corrupt-start-date rows.
    df["progress_gap_pct"] = df["progress_gap_pct"].fillna(0)
    df["time_elapsed_pct"] = df["time_elapsed_pct"].fillna(0)
    return df.set_index("project_id", drop=False)


def source_row(project_id: str) -> pd.Series | None:
    df = projects_frame()
    return df.loc[project_id] if project_id in df.index else None


def apply_scenario(
    row: pd.Series,
    physical_progress: float | None = None,
    expenditure_pct: float | None = None,
    milestone_recovery: str = "none",
) -> pd.DataFrame:
    """Returns a one-row frame with the scenario's inputs and derived fields rewritten."""
    r = row.copy()
    if physical_progress is not None:
        r["physical_progress"] = float(physical_progress)
        r["progress_gap_pct"] = float(physical_progress) - float(r["time_elapsed_pct"])
    if expenditure_pct is not None:
        r["expenditure_pct_of_revised_cost"] = float(expenditure_pct)
        r["expenditure"] = float(expenditure_pct) / 100.0 * float(r["revised_cost"])
    recovery = RECOVERY_FACTORS.get(milestone_recovery, 0.0)
    if recovery:
        r["delay_months"] = float(r["delay_months"]) * (1 - recovery)
        # Slippage is derived from revised/planned completion dates inside
        # add_engineered_columns; scale it via the revised date instead.
        revised, planned = pd.to_datetime(r["revised_completion"]), pd.to_datetime(r["planned_completion"])
        if pd.notna(revised) and pd.notna(planned):
            r["revised_completion"] = planned + (revised - planned) * (1 - recovery)
    return pd.DataFrame([r])


def predict(frame: pd.DataFrame, milestone_recovery: str = "none") -> Prediction:
    d_art, c_art = delay_artifact(), cost_artifact()
    X_delay = build_delay_features(frame, d_art["categories"])
    X_cost = build_cost_features(frame, c_art["categories"])

    delay_prob = float(d_art["classifier"].predict_proba(X_delay)[:, 1][0])
    delay_months = float(max(0.0, d_art["regressor"].predict(X_delay)[0]))
    delay_months *= 1 - RECOVERY_FACTORS.get(milestone_recovery, 0.0)
    cost_prob = float(c_art["classifier"].predict_proba(X_cost)[:, 1][0])
    escalation_pct = float(c_art["regressor"].predict(X_cost)[0])

    row = frame.iloc[0]
    original, revised = float(row["original_cost"]), float(row["revised_cost"])
    final_cost = max(original * (1 + escalation_pct / 100), revised)

    score, _, _ = risk_engine.risk_score(
        delay_prob,
        cost_prob,
        float(row["progress_gap_pct"]),
        float(row["physical_progress"]),
        float(row["expenditure_pct_of_revised_cost"]),
    )
    return Prediction(
        delay_probability=round(delay_prob, 4),
        predicted_delay_months=int(round(delay_months)),
        cost_overrun_probability=round(cost_prob, 4),
        predicted_final_cost_crore=round(final_cost, 2),
        risk_score=round(score, 1),
        risk_level=risk_engine.risk_level(score),
    )


def model_info() -> dict:
    d_art, c_art = delay_artifact(), cost_artifact()
    return {"delay": d_art, "cost": c_art}
