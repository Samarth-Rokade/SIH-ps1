"""What-if simulator: re-scores a project under hypothetical interventions by
re-running the trained delay/cost models and the risk formula on modified inputs.
"""
from __future__ import annotations

import math

from sqlalchemy.orm import Session

from app.database.models import Project
from app.database.schemas import (
    MilestoneRecoveryOptions,
    SimulationChange,
    SimulationOutcome,
    SimulationResult,
    SimulatorParameters,
    SimulatorRequest,
    SliderParameter,
)
from app.ml import predictor
from app.utils.response import ApiError

MAX_EXPENDITURE_PCT = 300.0  # some projects have already spent above 100% of revised cost

DISCLAIMER = (
    "Model-based scenario simulation, not a guaranteed outcome. Milestone recovery "
    "is a modeled assumption (share of schedule slippage recovered)."
)


def _get_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    return project


def get_parameters(db: Session, project_id: str) -> SimulatorParameters:
    project = _get_project(db, project_id)
    return SimulatorParameters(
        project_id=project.project_id,
        project_name=project.project_name,
        physical_progress=SliderParameter(current=round(project.physical_progress, 1), min=0, max=100),
        expenditure_percentage=SliderParameter(
            current=round(project.expenditure_pct_of_revised_cost, 1),
            min=0,
            max=max(100.0, math.ceil(project.expenditure_pct_of_revised_cost / 10) * 10),
        ),
        milestone_recovery=MilestoneRecoveryOptions(options=["none", "low", "medium", "high"], current="none"),
    )


def _outcome(p: predictor.Prediction) -> SimulationOutcome:
    return SimulationOutcome(
        risk_score=p.risk_score,
        risk_level=p.risk_level,
        delay_probability=p.delay_probability,
        predicted_delay_months=p.predicted_delay_months,
        predicted_cost_crore=p.predicted_final_cost_crore,
    )


def run(db: Session, request: SimulatorRequest) -> SimulationResult:
    project = _get_project(db, request.project_id)
    row = predictor.source_row(request.project_id)
    if row is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"No source data for project {request.project_id}")

    expenditure_pct = request.expenditure_percentage
    if expenditure_pct is None:
        expenditure_pct = request.monthly_expenditure
    for name, value, upper in (
        ("physical_progress", request.physical_progress, 100.0),
        ("expenditure_percentage", expenditure_pct, MAX_EXPENDITURE_PCT),
    ):
        if value is not None and not 0 <= value <= upper:
            raise ApiError(422, "INVALID_PARAMETER", f"{name} must be between 0 and {upper:g}")

    baseline = predictor.predict(predictor.apply_scenario(row))
    simulated = predictor.predict(
        predictor.apply_scenario(row, request.physical_progress, expenditure_pct, request.milestone_recovery),
        milestone_recovery=request.milestone_recovery,
    )
    return SimulationResult(
        project_id=project.project_id,
        project_name=project.project_name,
        baseline=_outcome(baseline),
        simulation=_outcome(simulated),
        change=SimulationChange(
            risk_reduction=round(baseline.risk_score - simulated.risk_score, 1),
            delay_reduction_months=baseline.predicted_delay_months - simulated.predicted_delay_months,
            cost_reduction_crore=round(baseline.predicted_final_cost_crore - simulated.predicted_final_cost_crore, 2),
        ),
        disclaimer=DISCLAIMER,
    )
