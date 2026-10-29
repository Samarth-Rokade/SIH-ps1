"""Pydantic response schemas matching the shapes in
docs/PAIMANA_Sentinel_AI_Backend_API_Specification.md.

Services build these (validation + a stable contract); routes just wrap
`model.model_dump(mode="json")` in the {success, data, meta} envelope.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

RiskLevel = Literal["critical", "high", "medium", "low"]


class DashboardOverview(BaseModel):
    total_projects: int
    critical_projects: int
    high_risk_projects: int
    medium_risk_projects: int
    low_risk_projects: int
    cost_exposure_crore: float
    average_delay_risk: float
    projects_needing_intervention: int
    data_as_of: date


class RiskMapPoint(BaseModel):
    project_id: str
    project_name: str
    state: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: RiskLevel
    delay_probability: float


class RiskDistributionBucket(BaseModel):
    level: RiskLevel
    count: int
    percentage: float


class RiskDistribution(BaseModel):
    total: int
    distribution: list[RiskDistributionBucket]


class RiskTrendPoint(BaseModel):
    month: str
    critical: int
    high: int
    medium: int
    low: int


class PriorityProject(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    risk_score: float
    risk_level: RiskLevel
    predicted_delay_months: int
    trend: Literal["increasing", "stable", "decreasing"]


class RiskRadarPoint(BaseModel):
    project_id: str
    project_name: str
    risk_score: float
    delay_probability: float
    cost_risk: float
    sector: str
    state: str


class RiskSummary(BaseModel):
    average_risk: float
    critical: int
    high: int
    medium: int
    low: int
    average_delay_probability: float
    average_cost_risk: float


class ProjectListItem(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    state: str
    original_cost_crore: float
    current_cost_crore: float
    physical_progress: float
    risk_score: float
    risk_level: RiskLevel
    predicted_delay_months: int


class ProjectDetail(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    state: str
    original_cost_crore: float
    current_cost_crore: float
    expenditure_crore: float
    physical_progress: float
    start_date: date
    original_completion_date: date
    current_completion_date: date | None
    status: str
    risk_score: float
    risk_level: RiskLevel


class RiskDetail(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    delay_probability: float
    cost_overrun_probability: float
    progress_risk: float
    financial_risk: float
    confidence: float


class PredictionRange(BaseModel):
    lower: int
    upper: int


class DelayPrediction(BaseModel):
    delay_probability: float
    predicted_delay_months: int
    prediction_range: PredictionRange
    risk_level: RiskLevel
    model: str


class CostPrediction(BaseModel):
    original_cost_crore: float
    current_cost_crore: float
    predicted_final_cost_crore: float
    expected_escalation_percentage: float
    additional_exposure_crore: float
    confidence: float


class RiskDriver(BaseModel):
    feature: str
    value: float
    impact: float
    direction: Literal["increases", "decreases"]


class RiskDrivers(BaseModel):
    risk_score: float
    drivers: list[RiskDriver]


class AlertListItem(BaseModel):
    alert_id: str
    project_id: str
    project_name: str
    severity: Literal["critical", "high", "medium"]
    risk_score: float
    alert_type: str
    message: str
    detected_at: date
    status: Literal["new", "acknowledged", "resolved"] = "new"


class AlertDetail(BaseModel):
    alert_id: str
    project_id: str
    severity: Literal["critical", "high", "medium"]
    type: str
    title: str
    description: str
    detected_at: date
    status: Literal["new", "acknowledged", "resolved"] = "new"
    risk_before: float
    risk_current: float
    recommended_review: str


class AlertSummary(BaseModel):
    critical: int
    high: int
    medium: int
    new: int
    resolved: int


class AlertUpdateRequest(BaseModel):
    status: Literal["new", "acknowledged", "resolved"]


class AlertUpdateResult(BaseModel):
    alert_id: str
    status: Literal["new", "acknowledged", "resolved"]


# --- Project intelligence (history / timeline / benchmark) -------------------


class ProgressPoint(BaseModel):
    month: str
    planned_progress: float
    actual_progress: float


class CostHistoryPoint(BaseModel):
    month: str
    original_cost: float
    current_cost: float
    expenditure: float


class TimelineEvent(BaseModel):
    name: str
    date: date
    status: Literal["completed", "delayed", "upcoming", "predicted"]


class ProjectTimeline(BaseModel):
    start_date: date
    planned_end_date: date
    predicted_end_date: date
    events: list[TimelineEvent]


class BenchmarkProject(BaseModel):
    risk: float
    progress: float
    expenditure_percentage: float


class BenchmarkPeers(BaseModel):
    count: int
    average_risk: float
    average_progress: float
    average_expenditure_percentage: float
    basis: str


class BenchmarkComparison(BaseModel):
    risk_difference: float
    progress_difference: float
    expenditure_difference: float


class ProjectBenchmark(BaseModel):
    project: BenchmarkProject
    similar_projects: BenchmarkPeers
    comparison: BenchmarkComparison


# --- Analytics ----------------------------------------------------------------


class MinistryAnalytics(BaseModel):
    ministry: str
    projects: int
    average_risk: float
    high_risk_percentage: float
    average_delay_months: float
    cost_escalation_percentage: float


class SectorAnalytics(BaseModel):
    sector: str
    projects: int
    average_risk: float
    high_risk_percentage: float


class StateAnalytics(BaseModel):
    state: str
    projects: int
    average_risk: float
    critical_projects: int


class CostSectorBreakdown(BaseModel):
    sector: str
    original_cost_crore: float
    current_cost_crore: float
    predicted_final_cost_crore: float


class CostExposureProject(BaseModel):
    project_id: str
    project_name: str
    sector: str
    ministry: str
    current_cost_crore: float
    predicted_final_cost_crore: float
    additional_exposure_crore: float
    expected_escalation_percentage: float


class CostAnalytics(BaseModel):
    total_original_cost_crore: float
    total_current_cost_crore: float
    total_expenditure_crore: float
    total_predicted_final_cost_crore: float
    average_escalation_percentage: float
    projects_with_escalation: int
    by_sector: list[CostSectorBreakdown]
    top_exposure_projects: list[CostExposureProject]


# --- What-if simulator -----------------------------------------------------------


class SliderParameter(BaseModel):
    current: float
    min: float
    max: float


class MilestoneRecoveryOptions(BaseModel):
    options: list[str]
    current: str = "none"


class SimulatorParameters(BaseModel):
    project_id: str
    project_name: str
    physical_progress: SliderParameter
    expenditure_percentage: SliderParameter
    milestone_recovery: MilestoneRecoveryOptions


class SimulatorRequest(BaseModel):
    project_id: str
    physical_progress: float | None = None
    expenditure_percentage: float | None = None
    # The API spec's example names this field `monthly_expenditure`; accept it as
    # an alias for the expenditure percentage so either request shape works.
    monthly_expenditure: float | None = None
    milestone_recovery: Literal["none", "low", "medium", "high"] = "none"


class SimulationOutcome(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    delay_probability: float
    predicted_delay_months: int
    predicted_cost_crore: float


class SimulationChange(BaseModel):
    risk_reduction: float
    delay_reduction_months: int
    cost_reduction_crore: float


class SimulationResult(BaseModel):
    project_id: str
    project_name: str
    baseline: SimulationOutcome
    simulation: SimulationOutcome
    change: SimulationChange
    disclaimer: str


# --- AI assistant ---------------------------------------------------------------


class AssistantRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    # Optional focus project (e.g. when asked from a project's page).
    project_id: str | None = None


class AssistantSource(BaseModel):
    project_id: str
    project_name: str


class AssistantResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[AssistantSource]
    engine: str


# --- Reports ------------------------------------------------------------------------


class ReportRequest(BaseModel):
    format: Literal["pdf"] = "pdf"


class DashboardReportRequest(BaseModel):
    month: str | None = None
    format: Literal["pdf"] = "pdf"


class ReportInfo(BaseModel):
    report_id: str
    kind: Literal["project", "dashboard"]
    title: str
    status: str
    created_at: str
    download_url: str
