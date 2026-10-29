from __future__ import annotations

import json

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectPrediction
from app.database.schemas import (
    CostPrediction,
    DelayPrediction,
    PredictionRange,
    ProjectDetail,
    ProjectListItem,
    RiskDetail,
    RiskDriver,
    RiskDrivers,
)
from app.ml import risk_engine
from app.utils.constants import DELAY_MODEL_NAME

SORTABLE_COLUMNS = {
    "risk_score": ProjectPrediction.risk_score,
    "physical_progress": Project.physical_progress,
    "original_cost_crore": Project.original_cost_crore,
    "current_cost_crore": Project.current_cost_crore,
    "project_name": Project.project_name,
}


def _joined_query(db: Session):
    return db.query(Project, ProjectPrediction).join(
        ProjectPrediction, Project.project_id == ProjectPrediction.project_id
    )


def _get_row(db: Session, project_id: str) -> tuple[Project, ProjectPrediction] | None:
    return _joined_query(db).filter(Project.project_id == project_id).first()


def list_projects(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    ministry: str | None,
    sector: str | None,
    state: str | None,
    risk_level: str | None,
    status: str | None,
    sort_by: str,
    sort_order: str,
) -> tuple[list[ProjectListItem], int]:
    query = _joined_query(db)
    if search:
        query = query.filter(Project.project_name.ilike(f"%{search}%"))
    if ministry:
        query = query.filter(Project.ministry == ministry)
    if sector:
        query = query.filter(Project.sector == sector)
    if state:
        query = query.filter(Project.state == state)
    if risk_level:
        query = query.filter(ProjectPrediction.risk_level == risk_level)
    if status:
        query = query.filter(Project.status == status)

    total = query.count()

    order_column = SORTABLE_COLUMNS.get(sort_by, ProjectPrediction.risk_score)
    order_fn = asc if sort_order == "asc" else desc
    query = query.order_by(order_fn(order_column))

    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [
        ProjectListItem(
            project_id=project.project_id,
            project_name=project.project_name,
            ministry=project.ministry,
            sector=project.sector,
            state=project.state,
            original_cost_crore=project.original_cost_crore,
            current_cost_crore=project.current_cost_crore,
            physical_progress=project.physical_progress,
            risk_score=prediction.risk_score,
            risk_level=prediction.risk_level,
            predicted_delay_months=prediction.predicted_delay_months,
        )
        for project, prediction in rows
    ]
    return items, total


def get_project(db: Session, project_id: str) -> ProjectDetail | None:
    row = _get_row(db, project_id)
    if row is None:
        return None
    project, prediction = row
    return ProjectDetail(
        project_id=project.project_id,
        project_name=project.project_name,
        ministry=project.ministry,
        sector=project.sector,
        state=project.state,
        original_cost_crore=project.original_cost_crore,
        current_cost_crore=project.current_cost_crore,
        expenditure_crore=project.expenditure_crore,
        physical_progress=project.physical_progress,
        start_date=project.start_date,
        original_completion_date=project.original_completion_date,
        current_completion_date=project.current_completion_date,
        status=project.status,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
    )


def get_risk(db: Session, project_id: str) -> RiskDetail | None:
    row = _get_row(db, project_id)
    if row is None:
        return None
    _, prediction = row
    return RiskDetail(
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        delay_probability=prediction.delay_probability,
        cost_overrun_probability=prediction.cost_overrun_probability,
        progress_risk=prediction.progress_risk,
        financial_risk=prediction.financial_risk,
        confidence=prediction.confidence,
    )


def get_delay_prediction(db: Session, project_id: str) -> DelayPrediction | None:
    row = _get_row(db, project_id)
    if row is None:
        return None
    _, prediction = row
    return DelayPrediction(
        delay_probability=prediction.delay_probability,
        predicted_delay_months=prediction.predicted_delay_months,
        prediction_range=PredictionRange(
            lower=prediction.delay_range_lower, upper=prediction.delay_range_upper
        ),
        risk_level=prediction.risk_level,
        model=DELAY_MODEL_NAME,
    )


def get_cost_prediction(db: Session, project_id: str) -> CostPrediction | None:
    row = _get_row(db, project_id)
    if row is None:
        return None
    project, prediction = row
    return CostPrediction(
        original_cost_crore=project.original_cost_crore,
        current_cost_crore=project.current_cost_crore,
        predicted_final_cost_crore=prediction.predicted_final_cost_crore,
        expected_escalation_percentage=prediction.expected_escalation_pct,
        additional_exposure_crore=prediction.additional_exposure_crore,
        confidence=risk_engine.confidence_from_probability(prediction.cost_overrun_probability),
    )


def get_risk_drivers(db: Session, project_id: str) -> RiskDrivers | None:
    row = _get_row(db, project_id)
    if row is None:
        return None
    _, prediction = row
    drivers = [RiskDriver(**d) for d in json.loads(prediction.drivers_json)]
    return RiskDrivers(risk_score=prediction.risk_score, drivers=drivers)
