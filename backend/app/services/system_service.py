from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.models import Project
from app.ml import predictor
from app.services import llm_client
from app.utils.constants import COST_MODEL_NAME, DATA_AS_OF, DELAY_MODEL_NAME, MODEL_VERSION

DATA_SOURCE = "PAIMANA Flash Reports / public government data"


def get_status(db: Session) -> dict:
    try:
        db.execute(text("SELECT 1"))
        database = "healthy"
    except Exception:
        database = "unavailable"
    try:
        predictor.delay_artifact()
        predictor.cost_artifact()
        ml_service = "healthy"
    except Exception:
        ml_service = "unavailable"
    llm = "healthy" if llm_client.is_available() else "fallback"
    overall = "online" if database == "healthy" and ml_service == "healthy" else "degraded"
    return {
        "status": overall,
        "database": database,
        "ml_service": ml_service,
        "llm_service": llm,
        "llm_model": llm_client.model_name(),
        "llm_note": None if llm == "healthy" else "Ollama not detected - the assistant is using its built-in grounded answer engine.",
        "last_data_update": DATA_AS_OF.isoformat(),
    }


def get_data_info(db: Session) -> dict:
    total = db.query(Project).count()
    return {
        "data_as_of": DATA_AS_OF.isoformat(),
        "total_projects": total,
        "source": DATA_SOURCE,
        "last_processed": predictor.delay_artifact()["trained_at"],
        "records_processed": total,
    }


def get_models() -> dict:
    delay, cost = predictor.delay_artifact(), predictor.cost_artifact()
    return {
        "delay_model": {
            "name": DELAY_MODEL_NAME,
            "version": MODEL_VERSION,
            "last_trained": delay["trained_at"][:10],
            "validation_auc": round(delay["validation_auc"], 3),
            "validation_mae": round(delay["validation_mae"], 2),
        },
        "cost_model": {
            "name": COST_MODEL_NAME,
            "version": MODEL_VERSION,
            "last_trained": cost["trained_at"][:10],
            "validation_auc": round(cost["validation_auc"], 3),
            "validation_mae": round(cost["validation_mae"], 2),
        },
        "explainability": "SHAP TreeExplainer on the delay classifier",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
