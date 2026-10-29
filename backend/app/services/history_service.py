"""Per-project progress / cost history, timeline and peer benchmark.

The source data (projects.csv) is a single monthly snapshot, so there are no
real historical series. The progress and cost histories are therefore *modeled
backfills*: smooth curves that end exactly at each project's real current
values, with small deterministic per-project variation. The API flags this via
`meta.modeled = true` and the UI labels them accordingly (same approach as the
dashboard risk trend).
"""
from __future__ import annotations

import calendar
import zlib
from datetime import date

import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectPrediction
from app.database.schemas import (
    BenchmarkComparison,
    BenchmarkPeers,
    BenchmarkProject,
    CostHistoryPoint,
    ProgressPoint,
    ProjectBenchmark,
    ProjectTimeline,
    TimelineEvent,
)
from app.utils.constants import DATA_AS_OF

HISTORY_MONTHS = 12
MIN_PEERS = 5


def add_months(d: date, months: int) -> date:
    index = d.year * 12 + (d.month - 1) + months
    year, month = divmod(index, 12)
    return date(year, month + 1, min(d.day, calendar.monthrange(year, month + 1)[1]))


def _month_ends(start: date) -> list[date]:
    """Month-end sample dates from max(start, 11 months ago) up to DATA_AS_OF."""
    first = max(start, add_months(DATA_AS_OF, -(HISTORY_MONTHS - 1)))
    points: list[date] = []
    cursor = date(first.year, first.month, 1)
    while cursor <= DATA_AS_OF:
        last_day = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        points.append(min(last_day, DATA_AS_OF))
        cursor = add_months(cursor, 1)
    return points


def _rng(project_id: str, salt: int) -> np.random.Generator:
    return np.random.default_rng(zlib.crc32(project_id.encode()) + salt)


def _fraction_since_start(start: date, at: date) -> float:
    total = max(1, (DATA_AS_OF - start).days)
    return min(1.0, max(0.0, (at - start).days / total))


def _monotone_curve(project_id: str, salt: int, fractions: list[float], final_value: float, exponent: float) -> list[float]:
    jitter = _rng(project_id, salt).normal(0, 0.012, len(fractions))
    values = [max(0.0, final_value * (f ** exponent) * (1 + j)) for f, j in zip(fractions, jitter)]
    values = [min(final_value, float(v)) for v in np.maximum.accumulate(values)]
    values[-1] = final_value
    return values


def get_progress(db: Session, project_id: str) -> list[ProgressPoint] | None:
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        return None
    dates = _month_ends(project.start_date)
    planned_span = max(1, (project.original_completion_date - project.start_date).days)
    fractions = [_fraction_since_start(project.start_date, d) for d in dates]
    actual = _monotone_curve(project_id, 1, fractions, project.physical_progress, 1.15)
    return [
        ProgressPoint(
            month=d.strftime("%Y-%m"),
            planned_progress=round(min(100.0, max(0.0, (d - project.start_date).days / planned_span * 100)), 1),
            actual_progress=round(a, 1),
        )
        for d, a in zip(dates, actual)
    ]


def get_cost_history(db: Session, project_id: str) -> list[CostHistoryPoint] | None:
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        return None
    dates = _month_ends(project.start_date)
    fractions = [_fraction_since_start(project.start_date, d) for d in dates]
    spend = _monotone_curve(project_id, 2, fractions, project.expenditure_crore, 1.05)
    escalation = project.current_cost_crore - project.original_cost_crore
    points = []
    for i, (d, s) in enumerate(zip(dates, spend)):
        # Revisions land part-way through the window: cost steps up over the first
        # ~60% of it and is at the true current figure by the end.
        ramp = min(1.0, (i + 1) / max(1.0, len(dates) * 0.6))
        points.append(
            CostHistoryPoint(
                month=d.strftime("%Y-%m"),
                original_cost=round(project.original_cost_crore, 2),
                current_cost=round(project.original_cost_crore + escalation * ramp, 2),
                expenditure=round(s, 2),
            )
        )
    return points


def get_timeline(db: Session, project_id: str) -> ProjectTimeline | None:
    row = (
        db.query(Project, ProjectPrediction)
        .join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
        .filter(Project.project_id == project_id)
        .first()
    )
    if row is None:
        return None
    project, prediction = row

    start, planned_end = project.start_date, project.original_completion_date
    if project.actual_completion_date:
        predicted_end = project.actual_completion_date
    else:
        predicted_end = add_months(planned_end, prediction.predicted_delay_months)

    span_days = (planned_end - start).days
    events = [
        TimelineEvent(
            name="Project Start", date=start, status="completed" if start <= DATA_AS_OF else "upcoming"
        )
    ]
    for pct in (25, 50, 75):
        due = date.fromordinal(start.toordinal() + round(span_days * pct / 100))
        if project.physical_progress >= pct:
            status = "completed"
        elif due < DATA_AS_OF:
            status = "delayed"
        else:
            status = "upcoming"
        events.append(TimelineEvent(name=f"{pct}% Physical Progress", date=due, status=status))

    if project.status == "Completed" or project.actual_completion_date:
        end_status = "completed"
    elif planned_end < DATA_AS_OF:
        end_status = "delayed"
    else:
        end_status = "upcoming"
    events.append(TimelineEvent(name="Planned Completion", date=planned_end, status=end_status))
    if predicted_end != planned_end:
        events.append(
            TimelineEvent(
                name="Actual Completion" if project.actual_completion_date else "Predicted Completion",
                date=predicted_end,
                status="completed" if project.actual_completion_date else "predicted",
            )
        )
    events.sort(key=lambda e: e.date)
    return ProjectTimeline(
        start_date=start, planned_end_date=planned_end, predicted_end_date=predicted_end, events=events
    )


def get_benchmark(db: Session, project_id: str) -> ProjectBenchmark | None:
    row = (
        db.query(Project, ProjectPrediction)
        .join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
        .filter(Project.project_id == project_id)
        .first()
    )
    if row is None:
        return None
    project, prediction = row

    def peer_stats(*filters):
        return (
            db.query(
                func.count(),
                func.avg(ProjectPrediction.risk_score),
                func.avg(Project.physical_progress),
                func.avg(Project.expenditure_pct_of_revised_cost),
            )
            .select_from(Project)
            .join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
            .filter(Project.project_id != project_id, *filters)
            .one()
        )

    basis = f"{project.sector} projects under {project.ministry}"
    stats = peer_stats(Project.sector == project.sector, Project.ministry == project.ministry)
    if stats[0] < MIN_PEERS:
        basis = f"{project.sector} projects"
        stats = peer_stats(Project.sector == project.sector)
    if stats[0] < MIN_PEERS:
        basis = "all projects"
        stats = peer_stats()
    count, avg_risk, avg_progress, avg_exp = stats[0], stats[1] or 0.0, stats[2] or 0.0, stats[3] or 0.0

    own_exp = project.expenditure_pct_of_revised_cost
    return ProjectBenchmark(
        project=BenchmarkProject(
            risk=prediction.risk_score,
            progress=project.physical_progress,
            expenditure_percentage=round(own_exp, 1),
        ),
        similar_projects=BenchmarkPeers(
            count=count,
            average_risk=round(avg_risk, 1),
            average_progress=round(avg_progress, 1),
            average_expenditure_percentage=round(avg_exp, 1),
            basis=basis,
        ),
        comparison=BenchmarkComparison(
            risk_difference=round(prediction.risk_score - avg_risk, 1),
            progress_difference=round(project.physical_progress - avg_progress, 1),
            expenditure_difference=round(own_exp - avg_exp, 1),
        ),
    )
