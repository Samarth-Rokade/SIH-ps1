from __future__ import annotations

from sqlalchemy import case, extract, func
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectPrediction
from app.database.schemas import (
    CostAnalytics,
    CostExposureProject,
    CostSectorBreakdown,
    MinistryAnalytics,
    SectorAnalytics,
    StateAnalytics,
)

TOP_EXPOSURE_LIMIT = 10
HIGH_RISK_LEVELS = ("critical", "high")


def _high_risk_share():
    """SQL average of 1/0 for critical-or-high, expressed as a percentage."""
    return func.avg(case((ProjectPrediction.risk_level.in_(HIGH_RISK_LEVELS), 100.0), else_=0.0))


def _joined(db: Session, *columns):
    return (
        db.query(*columns)
        .select_from(Project)
        .join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
    )


def get_ministries(db: Session) -> list[MinistryAnalytics]:
    rows = (
        _joined(
            db,
            Project.ministry,
            func.count(),
            func.avg(ProjectPrediction.risk_score),
            _high_risk_share(),
            func.avg(ProjectPrediction.predicted_delay_months),
            func.avg(ProjectPrediction.expected_escalation_pct),
        )
        .group_by(Project.ministry)
        .order_by(func.avg(ProjectPrediction.risk_score).desc())
        .all()
    )
    return [
        MinistryAnalytics(
            ministry=ministry,
            projects=count,
            average_risk=round(avg_risk, 1),
            high_risk_percentage=round(high_share, 1),
            average_delay_months=round(avg_delay, 1),
            cost_escalation_percentage=round(avg_esc, 1),
        )
        for ministry, count, avg_risk, high_share, avg_delay, avg_esc in rows
    ]


def get_sectors(db: Session) -> list[SectorAnalytics]:
    rows = (
        _joined(db, Project.sector, func.count(), func.avg(ProjectPrediction.risk_score), _high_risk_share())
        .group_by(Project.sector)
        .order_by(func.avg(ProjectPrediction.risk_score).desc())
        .all()
    )
    return [
        SectorAnalytics(
            sector=sector, projects=count, average_risk=round(avg_risk, 1), high_risk_percentage=round(high_share, 1)
        )
        for sector, count, avg_risk, high_share in rows
    ]


def get_states(db: Session) -> list[StateAnalytics]:
    rows = (
        _joined(
            db,
            Project.state,
            func.count(),
            func.avg(ProjectPrediction.risk_score),
            func.sum(case((ProjectPrediction.risk_level == "critical", 1), else_=0)),
        )
        .group_by(Project.state)
        .order_by(func.avg(ProjectPrediction.risk_score).desc())
        .all()
    )
    return [
        StateAnalytics(state=state, projects=count, average_risk=round(avg_risk, 1), critical_projects=int(critical or 0))
        for state, count, avg_risk, critical in rows
    ]


def get_cost(db: Session, sector: str | None, ministry: str | None, year: int | None) -> CostAnalytics:
    filters = []
    if sector:
        filters.append(Project.sector == sector)
    if ministry:
        filters.append(Project.ministry == ministry)
    if year:
        filters.append(extract("year", Project.start_date) == year)

    totals = (
        _joined(
            db,
            func.coalesce(func.sum(Project.original_cost_crore), 0.0),
            func.coalesce(func.sum(Project.current_cost_crore), 0.0),
            func.coalesce(func.sum(Project.expenditure_crore), 0.0),
            func.coalesce(func.sum(ProjectPrediction.predicted_final_cost_crore), 0.0),
            # Realized escalation: revised (current) cost against the original sanction.
            func.coalesce(
                func.avg((Project.current_cost_crore - Project.original_cost_crore) / Project.original_cost_crore * 100),
                0.0,
            ),
            func.coalesce(func.sum(case((Project.current_cost_crore > Project.original_cost_crore, 1), else_=0)), 0),
        )
        .filter(*filters)
        .one()
    )
    original, current, spent, predicted, avg_esc, with_esc = totals

    by_sector = (
        _joined(
            db,
            Project.sector,
            func.sum(Project.original_cost_crore),
            func.sum(Project.current_cost_crore),
            func.sum(ProjectPrediction.predicted_final_cost_crore),
        )
        .filter(*filters)
        .group_by(Project.sector)
        .order_by(func.sum(ProjectPrediction.predicted_final_cost_crore).desc())
        .all()
    )

    exposure_rows = (
        _joined(db, Project, ProjectPrediction)
        .filter(*filters)
        .order_by(ProjectPrediction.additional_exposure_crore.desc())
        .limit(TOP_EXPOSURE_LIMIT)
        .all()
    )

    return CostAnalytics(
        total_original_cost_crore=round(original, 1),
        total_current_cost_crore=round(current, 1),
        total_expenditure_crore=round(spent, 1),
        total_predicted_final_cost_crore=round(predicted, 1),
        average_escalation_percentage=round(avg_esc, 1),
        projects_with_escalation=int(with_esc),
        by_sector=[
            CostSectorBreakdown(
                sector=name,
                original_cost_crore=round(o, 1),
                current_cost_crore=round(c, 1),
                predicted_final_cost_crore=round(p, 1),
            )
            for name, o, c, p in by_sector
        ],
        top_exposure_projects=[
            CostExposureProject(
                project_id=project.project_id,
                project_name=project.project_name,
                sector=project.sector,
                ministry=project.ministry,
                current_cost_crore=project.current_cost_crore,
                predicted_final_cost_crore=prediction.predicted_final_cost_crore,
                additional_exposure_crore=prediction.additional_exposure_crore,
                expected_escalation_percentage=prediction.expected_escalation_pct,
            )
            for project, prediction in exposure_rows
        ],
    )
