"""Train the delay prediction models.

Two models share one leak-safe feature set (ml/features.build_delay_features):
  - classifier -> delay_probability   (target: delay_label)
  - regressor  -> predicted_delay_months (target: delay_months)

Validated with a temporal split (README-recommended: train on projects that
started before 2023, test on later ones) to get an honest read on forward-looking
performance, then refit on the full clean dataset so every project can be scored.

Run from the project root:
    python ml/training/train_delay_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, roc_auc_score
from xgboost import XGBClassifier, XGBRegressor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.features import build_delay_features, category_map  # noqa: E402

DATA_PATH = ROOT / "data" / "projects.csv"
MODEL_DIR = ROOT / "ml" / "models"
SPLIT_DATE = "2023-01-01"

CLASSIFIER_PARAMS = dict(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    tree_method="hist",
    enable_categorical=True,
    eval_metric="auc",
    random_state=42,
)

REGRESSOR_PARAMS = dict(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    tree_method="hist",
    enable_categorical=True,
    random_state=42,
)


def load_clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["start_date"])
    return df[df["data_quality_flag"] == 0].reset_index(drop=True)


def main() -> None:
    df = load_clean_data()
    train_df = df[df["start_date"] < SPLIT_DATE]
    test_df = df[df["start_date"] >= SPLIT_DATE]
    print(f"Train rows: {len(train_df)}  Test rows: {len(test_df)}")

    # Fix categories from the full dataset so train/test splits agree on the
    # same set of possible ministry/sector/state/status values.
    categories = category_map(build_delay_features(df))
    X_train = build_delay_features(train_df, categories)
    X_test = build_delay_features(test_df, categories)
    y_clf_train, y_clf_test = train_df["delay_label"], test_df["delay_label"]
    y_reg_train, y_reg_test = train_df["delay_months"], test_df["delay_months"]

    clf = XGBClassifier(**CLASSIFIER_PARAMS)
    clf.fit(X_train, y_clf_train)
    val_probs = clf.predict_proba(X_test)[:, 1]
    val_auc = roc_auc_score(y_clf_test, val_probs)
    print(f"Validation AUC (delay classifier): {val_auc:.4f}")

    reg = XGBRegressor(**REGRESSOR_PARAMS)
    reg.fit(X_train, y_reg_train)
    val_preds = reg.predict(X_test)
    val_mae = mean_absolute_error(y_reg_test, val_preds)
    residual_std = float(np.std(y_reg_test.to_numpy() - val_preds))
    print(f"Validation MAE (delay months): {val_mae:.2f}  residual_std: {residual_std:.2f}")

    # Refit on the full clean dataset so every project gets a prediction.
    X_full = build_delay_features(df, categories)
    clf_full = XGBClassifier(**CLASSIFIER_PARAMS)
    clf_full.fit(X_full, df["delay_label"])
    reg_full = XGBRegressor(**REGRESSOR_PARAMS)
    reg_full.fit(X_full, df["delay_months"])

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "classifier": clf_full,
            "regressor": reg_full,
            "residual_std": residual_std,
            "validation_auc": val_auc,
            "validation_mae": val_mae,
            "feature_columns": list(X_full.columns),
            "categories": categories,
            "trained_at": pd.Timestamp.now("UTC").isoformat(),
        },
        MODEL_DIR / "delay_model.pkl",
    )
    print(f"Saved {MODEL_DIR / 'delay_model.pkl'}")


if __name__ == "__main__":
    main()
