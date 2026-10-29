from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import AlertUpdateRequest
from app.services import alert_service
from app.utils.response import ApiError, success

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    severity: str | None = Query(default=None),
    state: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items, total = alert_service.list_alerts(db, page, page_size, severity, state, sector, status)
    return success([item.model_dump(mode="json") for item in items], meta={"total": total})


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return success(alert_service.get_summary(db).model_dump(mode="json"))


@router.get("/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if alert is None:
        raise ApiError(404, "ALERT_NOT_FOUND", f"Alert with ID {alert_id} was not found")
    return success(alert.model_dump(mode="json"))


@router.patch("/{alert_id}")
def update_alert(alert_id: str, body: AlertUpdateRequest, db: Session = Depends(get_db)):
    result = alert_service.update_status(db, alert_id, body.status)
    if result is None:
        raise ApiError(404, "ALERT_NOT_FOUND", f"Alert with ID {alert_id} was not found")
    return success(result.model_dump(mode="json"))
