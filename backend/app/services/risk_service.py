from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectPrediction
from app.database.schemas import RiskRadarPoint, RiskSummary


def get_radar(
    db: Session,
    ministry: str | None,
    sector: str | None,
    state: str | None,
    risk_level: str | None,
    limit: int,
) -> list[RiskRadarPoint]:
    query = db.query(Project, ProjectPrediction).join(
        ProjectPrediction, Project.project_id == ProjectPrediction.project_id
    )
    if ministry:
        query = query.filter(Project.ministry == ministry)
    if sector:
        query = query.filter(Project.sector == sector)
    if state:
        query = query.filter(Project.state == state)
    if risk_level:
        query = query.filter(ProjectPrediction.risk_level == risk_level)

    rows = query.order_by(ProjectPrediction.risk_score.desc()).limit(limit).all()
    return [
        RiskRadarPoint(
            project_id=project.project_id,
            project_name=project.project_name,
            risk_score=prediction.risk_score,
            delay_probability=prediction.delay_probability,
            cost_risk=prediction.cost_overrun_probability,
            sector=project.sector,
            state=project.state,
        )
        for project, prediction in rows
    ]


def get_summary(db: Session) -> RiskSummary:
    counts = {
        level: db.query(ProjectPrediction).filter(ProjectPrediction.risk_level == level).count()
        for level in ("critical", "high", "medium", "low")
    }
    avg_risk = db.query(func.avg(ProjectPrediction.risk_score)).scalar() or 0.0
    avg_delay = db.query(func.avg(ProjectPrediction.delay_probability)).scalar() or 0.0
    avg_cost = db.query(func.avg(ProjectPrediction.cost_overrun_probability)).scalar() or 0.0

    return RiskSummary(
        average_risk=round(avg_risk, 1),
        critical=counts["critical"],
        high=counts["high"],
        medium=counts["medium"],
        low=counts["low"],
        average_delay_probability=round(avg_delay, 3),
        average_cost_risk=round(avg_cost, 3),
    )
