from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import dashboard_service
from app.utils.response import success

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return success(dashboard_service.get_overview(db).model_dump(mode="json"))


@router.get("/risk-map")
def risk_map(
    risk_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    points = dashboard_service.get_risk_map(db, risk_level)
    return success([p.model_dump(mode="json") for p in points])


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    return success(dashboard_service.get_risk_distribution(db).model_dump(mode="json"))


@router.get("/risk-trend")
def risk_trend(months: int = Query(default=6, ge=1, le=24), db: Session = Depends(get_db)):
    points = dashboard_service.get_risk_trend(db, months)
    return success([p.model_dump(mode="json") for p in points])


@router.get("/priority-projects")
def priority_projects(limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    points = dashboard_service.get_priority_projects(db, limit)
    return success([p.model_dump(mode="json") for p in points])
