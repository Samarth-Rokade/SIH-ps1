from datetime import date

# projects.csv derived fields are all computed relative to the PAIMANA Flash
# Report reference month (see data/README.md); reused wherever the backend
# needs a stable "as of" date (dashboard overview, alerts, risk trend).
DATA_AS_OF = date(2026, 7, 31)

DELAY_MODEL_NAME = "XGBoost Classifier"
COST_MODEL_NAME = "XGBoost Regressor"

MODEL_VERSION = "1.0"

# Local LLM (Ollama). The assistant falls back to a built-in, database-grounded
# answer engine when no Ollama server is reachable, so the app never depends on it.
OLLAMA_URL_ENV = "OLLAMA_URL"
OLLAMA_MODEL_ENV = "OLLAMA_MODEL"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
