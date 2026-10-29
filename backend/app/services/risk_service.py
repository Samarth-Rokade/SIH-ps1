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
    # Column-only query: building full ORM entities for thousands of rows is the
    # slow part of this endpoint, and the radar needs just these fields.
    query = db.query(
        Project.project_id,
        Project.project_name,
        ProjectPrediction.risk_score,
        ProjectPrediction.delay_probability,
        ProjectPrediction.cost_overrun_probability,
        Project.sector,
        Project.state,
    ).join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
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
            project_id=pid,
            project_name=name,
            risk_score=score,
            delay_probability=delay,
            cost_risk=cost,
            sector=sector_name,
            state=state_name,
        )
        for pid, name, score, delay, cost, sector_name, state_name in rows
    ]


def get_filter_options(db: Session) -> dict[str, list[str]]:
    """Distinct values for the filter dropdowns (avoids fetching every radar point just to list them)."""

    def distinct(column) -> list[str]:
        return sorted(v for (v,) in db.query(column).distinct().all())

    return {
        "sectors": distinct(Project.sector),
        "states": distinct(Project.state),
        "ministries": distinct(Project.ministry),
    }


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
