"""SHAP-based risk driver explanations (API spec S20 / S6 PHASE 6).

Explains the *delay* classifier's prediction for each project (the largest
weight in the risk formula) as a handful of human-readable "top reasons",
each carrying a share of the project's overall risk score.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier

DISPLAY_LABELS: dict[str, str] = {
    "progress_gap_pct": "Progress Gap",
    "expenditure_pct_of_original_cost": "Expenditure Utilization",
    "expenditure_pct_of_revised_cost": "Expenditure vs Revised Cost",
    "time_elapsed_pct": "Time Elapsed vs Plan",
    "project_age_months": "Project Age",
    "burn_rate": "Monthly Spending Rate",
    "original_cost": "Project Cost",
    "physical_progress": "Physical Progress",
    "planned_duration_months": "Planned Duration",
    "elapsed_months": "Elapsed Time",
    "expenditure": "Cumulative Expenditure",
    "delay_months": "Historical Schedule Slippage",
    "has_revised_completion": "Completion Date Revised",
    "schedule_slippage_months": "Milestone Slippage",
}

# Only numeric features are shown as top drivers (categorical SHAP values
# don't map to a meaningful display "value"), but all features still count
# toward the total used to normalize impact shares.
NUMERIC_ONLY_LABELS = set(DISPLAY_LABELS)

TOP_N_DRIVERS = 5


def compute_all_drivers(
    model: XGBClassifier,
    X: pd.DataFrame,
    risk_scores: np.ndarray,
) -> list[list[dict]]:
    """Batched SHAP explanation for every row in X, one driver list per row."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):  # some SHAP/model combos return [class0, class1]
        shap_values = shap_values[-1]

    numeric_col_positions = [
        i for i, col in enumerate(X.columns) if col in NUMERIC_ONLY_LABELS
    ]

    results: list[list[dict]] = []
    for row_idx in range(len(X)):
        row_shap = shap_values[row_idx]
        total_abs = float(np.abs(row_shap).sum()) or 1.0
        candidates = sorted(
            numeric_col_positions, key=lambda i: -abs(row_shap[i])
        )[:TOP_N_DRIVERS]

        drivers = []
        for col_idx in candidates:
            col = X.columns[col_idx]
            shap_val = float(row_shap[col_idx])
            impact = round(abs(shap_val) / total_abs * float(risk_scores[row_idx]))
            if impact <= 0:
                continue
            drivers.append(
                {
                    "feature": DISPLAY_LABELS.get(col, col),
                    "value": round(float(X.iloc[row_idx][col]), 1),
                    "impact": int(impact),
                    "direction": "increases" if shap_val > 0 else "decreases",
                }
            )
        results.append(drivers)
    return results
