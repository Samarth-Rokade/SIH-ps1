from datetime import date

# projects.csv derived fields are all computed relative to the PAIMANA Flash
# Report reference month (see data/README.md); reused wherever the backend
# needs a stable "as of" date (dashboard overview, alerts, risk trend).
DATA_AS_OF = date(2026, 7, 31)

DELAY_MODEL_NAME = "XGBoost Classifier"
COST_MODEL_NAME = "XGBoost Regressor"
