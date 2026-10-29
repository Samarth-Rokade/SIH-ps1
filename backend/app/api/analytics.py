from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import analytics_service
from app.utils.response import success

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/ministries")
def ministries(db: Session = Depends(get_db)):
    return success([m.model_dump(mode="json") for m in analytics_service.get_ministries(db)])


@router.get("/sectors")
def sectors(db: Session = Depends(get_db)):
    return success([s.model_dump(mode="json") for s in analytics_service.get_sectors(db)])


@router.get("/states")
def states(db: Session = Depends(get_db)):
    return success([s.model_dump(mode="json") for s in analytics_service.get_states(db)])


@router.get("/cost")
def cost(
    sector: str | None = Query(default=None),
    ministry: str | None = Query(default=None),
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return success(analytics_service.get_cost(db, sector, ministry, year).model_dump(mode="json"))
