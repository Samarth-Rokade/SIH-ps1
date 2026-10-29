from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectPrediction
from app.database.schemas import (
    DashboardOverview,
    PriorityProject,
    RiskDistribution,
    RiskDistributionBucket,
    RiskMapPoint,
    RiskTrendPoint,
)
from app.utils.constants import DATA_AS_OF

LEVELS = ["critical", "high", "medium", "low"]
# Modeled backfill: no historical snapshots exist in the source data, so this
# walks risk-level counts backward from the true current distribution with a
# smooth monthly drift, purely for the dashboard trend chart.
TREND_DRIFT_PER_MONTH = 0.035


def _level_counts(db: Session) -> dict[str, int]:
    rows = (
        db.query(ProjectPrediction.risk_level, func.count())
        .group_by(ProjectPrediction.risk_level)
        .all()
    )
    counts = {level: 0 for level in LEVELS}
    counts.update({level: count for level, count in rows})
    return counts


def get_overview(db: Session) -> DashboardOverview:
    total = db.query(Project).count()
    counts = _level_counts(db)

    exposure = (
        db.query(func.sum(ProjectPrediction.additional_exposure_crore))
        .filter(ProjectPrediction.additional_exposure_crore > 0)
        .scalar()
        or 0.0
    )
    avg_delay_risk = db.query(func.avg(ProjectPrediction.delay_probability)).scalar() or 0.0

    return DashboardOverview(
        total_projects=total,
        critical_projects=counts["critical"],
        high_risk_projects=counts["high"],
        medium_risk_projects=counts["medium"],
        low_risk_projects=counts["low"],
        cost_exposure_crore=round(exposure, 1),
        average_delay_risk=round(avg_delay_risk * 100, 1),
        projects_needing_intervention=counts["critical"] + counts["high"],
        data_as_of=DATA_AS_OF,
    )


def get_risk_map(db: Session, risk_level: str | None) -> list[RiskMapPoint]:
    # Column-only query (no ORM entities): this returns every project, so row
    # construction cost dominates.
    query = db.query(
        Project.project_id,
        Project.project_name,
        Project.state,
        Project.latitude,
        Project.longitude,
        ProjectPrediction.risk_score,
        ProjectPrediction.risk_level,
        ProjectPrediction.delay_probability,
    ).join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
    if risk_level and risk_level != "all":
        query = query.filter(ProjectPrediction.risk_level == risk_level)
    return [
        RiskMapPoint(
            project_id=pid,
            project_name=name,
            state=state,
            latitude=lat,
            longitude=lon,
            risk_score=score,
            risk_level=level,
            delay_probability=delay,
        )
        for pid, name, state, lat, lon, score, level, delay in query.all()
    ]


def get_risk_distribution(db: Session) -> RiskDistribution:
    counts = _level_counts(db)
    total = sum(counts.values()) or 1
    return RiskDistribution(
        total=total,
        distribution=[
            RiskDistributionBucket(
                level=level, count=counts[level], percentage=round(counts[level] / total * 100, 2)
            )
            for level in LEVELS
        ],
    )


def get_risk_trend(db: Session, months: int) -> list[RiskTrendPoint]:
    current = _level_counts(db)
    points: list[dict[str, int]] = []
    for k in range(months - 1, -1, -1):
        drift = TREND_DRIFT_PER_MONTH * k
        critical = round(current["critical"] * (1 - drift))
        high = round(current["high"] * (1 - drift * 0.8))
        medium = round(current["medium"] * (1 - drift * 0.3))
        shifted = (current["critical"] - critical) + (current["high"] - high) + (current["medium"] - medium)
        low = current["low"] + shifted
        points.append({"critical": critical, "high": high, "medium": medium, "low": low})
    points[-1] = current  # most recent month must equal the true current distribution

    labels = []
    year, month = DATA_AS_OF.year, DATA_AS_OF.month
    for _ in range(months):
        labels.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    labels.reverse()

    return [
        RiskTrendPoint(month=label, **point) for label, point in zip(labels, points)
    ]


def get_priority_projects(db: Session, limit: int) -> list[PriorityProject]:
    rows = (
        db.query(Project, ProjectPrediction)
        .join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
        .order_by(ProjectPrediction.risk_score.desc())
        .limit(limit)
        .all()
    )
    return [
        PriorityProject(
            project_id=project.project_id,
            project_name=project.project_name,
            ministry=project.ministry,
            risk_score=prediction.risk_score,
            risk_level=prediction.risk_level,
            predicted_delay_months=prediction.predicted_delay_months,
            trend=prediction.trend,
        )
        for project, prediction in rows
    ]
