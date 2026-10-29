from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import history_service, project_service
from app.utils.response import ApiError, success

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=4000),
    search: str | None = Query(default=None),
    ministry: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    state: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    status: str | None = Query(default=None),
    sort_by: str = Query(default="risk_score"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
):
    items, total = project_service.list_projects(
        db, page, page_size, search, ministry, sector, state, risk_level, status, sort_by, sort_order
    )
    total_pages = max(1, math.ceil(total / page_size))
    return success(
        [item.model_dump(mode="json") for item in items],
        meta={"page": page, "page_size": page_size, "total": total, "total_pages": total_pages},
    )


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if project is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return success(project.model_dump(mode="json"))


@router.get("/{project_id}/risk")
def get_risk(project_id: str, db: Session = Depends(get_db)):
    risk = project_service.get_risk(db, project_id)
    if risk is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return success(risk.model_dump(mode="json"))


@router.get("/{project_id}/prediction/delay")
def get_delay_prediction(project_id: str, db: Session = Depends(get_db)):
    prediction = project_service.get_delay_prediction(db, project_id)
    if prediction is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return success(prediction.model_dump(mode="json"))


@router.get("/{project_id}/prediction/cost")
def get_cost_prediction(project_id: str, db: Session = Depends(get_db)):
    prediction = project_service.get_cost_prediction(db, project_id)
    if prediction is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return success(prediction.model_dump(mode="json"))


@router.get("/{project_id}/risk-drivers")
def get_risk_drivers(project_id: str, db: Session = Depends(get_db)):
    drivers = project_service.get_risk_drivers(db, project_id)
    if drivers is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return success(drivers.model_dump(mode="json"))


def _or_404(result, project_id: str):
    if result is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return result


@router.get("/{project_id}/progress")
def get_progress(project_id: str, db: Session = Depends(get_db)):
    points = _or_404(history_service.get_progress(db, project_id), project_id)
    return success([p.model_dump(mode="json") for p in points], meta={"modeled": True})


@router.get("/{project_id}/cost-history")
def get_cost_history(project_id: str, db: Session = Depends(get_db)):
    points = _or_404(history_service.get_cost_history(db, project_id), project_id)
    return success([p.model_dump(mode="json") for p in points], meta={"modeled": True})


@router.get("/{project_id}/timeline")
def get_timeline(project_id: str, db: Session = Depends(get_db)):
    return success(_or_404(history_service.get_timeline(db, project_id), project_id).model_dump(mode="json"))


@router.get("/{project_id}/benchmark")
def get_benchmark(project_id: str, db: Session = Depends(get_db)):
    return success(_or_404(history_service.get_benchmark(db, project_id), project_id).model_dump(mode="json"))
