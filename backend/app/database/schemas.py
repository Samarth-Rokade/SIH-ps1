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


class AlertDetail(BaseModel):
    alert_id: str
    project_id: str
    severity: Literal["critical", "high", "medium"]
    type: str
    title: str
    description: str
    detected_at: date
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
