"""Shared leak-safe feature engineering for the delay and cost models.

Single source of truth used by both the offline training scripts
(ml/training/*.py) and the backend seed pipeline (backend/app/ml/seed.py),
so training-time and serving-time feature construction can never drift apart.

See data/README.md "Leakage warning" for why each column is excluded.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORICAL_COLUMNS = ["ministry", "sector", "state", "status"]

DELAY_NUMERIC_COLUMNS = [
    "original_cost",
    "expenditure",
    "physical_progress",
    "planned_duration_months",
    "elapsed_months",
    "time_elapsed_pct",
    "progress_gap_pct",
    "project_age_months",
    "expenditure_pct_of_original_cost",
    "burn_rate",
]

COST_NUMERIC_COLUMNS = [
    "original_cost",
    "expenditure",
    "physical_progress",
    "planned_duration_months",
    "elapsed_months",
    "time_elapsed_pct",
    "progress_gap_pct",
    "project_age_months",
    "expenditure_pct_of_revised_cost",
    "delay_months",
    "has_revised_completion",
    "schedule_slippage_months",
    "burn_rate",
]

DELAY_FEATURE_COLUMNS = CATEGORICAL_COLUMNS + DELAY_NUMERIC_COLUMNS
COST_FEATURE_COLUMNS = CATEGORICAL_COLUMNS + COST_NUMERIC_COLUMNS


def add_engineered_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns that aren't already present in projects.csv.

    Safe to call on the full dataset (training subset or full serving set) -
    only adds columns, never touches labels or leak columns.
    """
    df = df.copy()

    age_months_safe = df["project_age_months"].clip(lower=1)
    df["burn_rate"] = df["expenditure"] / age_months_safe

    df["expenditure_pct_of_original_cost"] = (
        df["expenditure"] / df["original_cost"].replace(0, np.nan) * 100
    ).fillna(0)

    revised_completion = pd.to_datetime(df["revised_completion"], errors="coerce")
    planned_completion = pd.to_datetime(df["planned_completion"], errors="coerce")
    df["has_revised_completion"] = revised_completion.notna().astype(int)
    slippage_days = (revised_completion - planned_completion).dt.days
    df["schedule_slippage_months"] = (slippage_days / 30).fillna(0)

    return df


def _prepare_categoricals(
    X: pd.DataFrame, categories: dict[str, list] | None = None
) -> pd.DataFrame:
    """Cast categorical columns to pandas 'category' dtype.

    A fixed `categories` map (derived from the full dataset) must be passed for
    any split narrower than the full data - otherwise a category value present
    only in the test/serving split but absent from train raises at predict time.
    """
    for col in CATEGORICAL_COLUMNS:
        if categories is not None:
            X[col] = pd.Categorical(X[col], categories=categories[col])
        else:
            X[col] = X[col].astype("category")
    return X


def category_map(X: pd.DataFrame) -> dict[str, list]:
    """Capture the categories of an already-categorical frame, for reuse on splits."""
    return {col: list(X[col].cat.categories) for col in CATEGORICAL_COLUMNS}


def build_delay_features(
    df: pd.DataFrame, categories: dict[str, list] | None = None
) -> pd.DataFrame:
    """Leak-safe feature matrix for the delay classifier/regressor."""
    df = add_engineered_columns(df)
    X = df[DELAY_FEATURE_COLUMNS].copy()
    return _prepare_categoricals(X, categories)


def build_cost_features(
    df: pd.DataFrame, categories: dict[str, list] | None = None
) -> pd.DataFrame:
    """Leak-safe feature matrix for the cost overrun classifier/regressor."""
    df = add_engineered_columns(df)
    X = df[COST_FEATURE_COLUMNS].copy()
    return _prepare_categoricals(X, categories)
