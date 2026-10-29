from __future__ import annotations

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    project_name: Mapped[str] = mapped_column(String)
    ministry: Mapped[str] = mapped_column(String, index=True)
    sector: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, index=True)

    original_cost_crore: Mapped[float] = mapped_column(Float)
    current_cost_crore: Mapped[float] = mapped_column(Float)  # revised_cost
    expenditure_crore: Mapped[float] = mapped_column(Float)
    physical_progress: Mapped[float] = mapped_column(Float)

    start_date: Mapped[str] = mapped_column(Date)
    original_completion_date: Mapped[str] = mapped_column(Date)
    current_completion_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    actual_completion_date: Mapped[str | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String)  # Ongoing / Completed
    data_source: Mapped[str] = mapped_column(String)
    data_quality_flag: Mapped[int] = mapped_column(Integer, default=0)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Fields carried straight from projects.csv, useful for display/derivations.
    progress_gap_pct: Mapped[float] = mapped_column(Float)
    time_elapsed_pct: Mapped[float] = mapped_column(Float)
    expenditure_pct_of_revised_cost: Mapped[float] = mapped_column(Float)
    project_age_months: Mapped[int] = mapped_column(Integer)

    prediction: Mapped["ProjectPrediction"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectPrediction(Base):
    __tablename__ = "project_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String, ForeignKey("projects.project_id"), unique=True, index=True
    )

    delay_probability: Mapped[float] = mapped_column(Float)
    predicted_delay_months: Mapped[int] = mapped_column(Integer)
    delay_range_lower: Mapped[int] = mapped_column(Integer)
    delay_range_upper: Mapped[int] = mapped_column(Integer)

    cost_overrun_probability: Mapped[float] = mapped_column(Float)
    predicted_final_cost_crore: Mapped[float] = mapped_column(Float)
    expected_escalation_pct: Mapped[float] = mapped_column(Float)
    additional_exposure_crore: Mapped[float] = mapped_column(Float)

    risk_score: Mapped[float] = mapped_column(Float, index=True)
    risk_level: Mapped[str] = mapped_column(String, index=True)
    progress_risk: Mapped[float] = mapped_column(Float)
    financial_risk: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)

    trend: Mapped[str] = mapped_column(String)  # heuristic: increasing/stable/decreasing
    drivers_json: Mapped[str] = mapped_column(String)  # JSON list of {feature,value,impact,direction}

    project: Mapped["Project"] = relationship(back_populates="prediction")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    project_id: Mapped[str] = mapped_column(
        String, ForeignKey("projects.project_id"), index=True
    )

    severity: Mapped[str] = mapped_column(String, index=True)  # critical/high/medium
    alert_type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    detected_at: Mapped[str] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default="new")  # new/acknowledged/resolved

    risk_before: Mapped[float] = mapped_column(Float)
    risk_current: Mapped[float] = mapped_column(Float)

    project: Mapped["Project"] = relationship(back_populates="alerts")
