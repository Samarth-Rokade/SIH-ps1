from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import risk_service
from app.utils.response import success

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/radar")
def radar(
    ministry: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    state: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    points = risk_service.get_radar(db, ministry, sector, state, risk_level, limit)
    return success([p.model_dump(mode="json") for p in points])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return success(risk_service.get_summary(db).model_dump(mode="json"))
