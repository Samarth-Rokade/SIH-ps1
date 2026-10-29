"""Weighted risk scoring engine (API spec S45).

    risk_score = 0.50 x delay_risk + 0.25 x cost_risk
               + 0.15 x progress_risk + 0.10 x financial_risk

These are prototype decision-support weights, not official MoSPI weights.
"""
from __future__ import annotations

DELAY_WEIGHT = 0.50
COST_WEIGHT = 0.25
PROGRESS_WEIGHT = 0.15
FINANCIAL_WEIGHT = 0.10

FINANCIAL_RISK_SCALE = 1.5  # amplifies spend/progress mismatch into a 0-100 risk score


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def progress_risk(progress_gap_pct: float) -> float:
    """Behind schedule (negative gap) increases risk; ahead of schedule doesn't."""
    return clamp(-progress_gap_pct)


def financial_risk(physical_progress: float, expenditure_pct_of_revised_cost: float) -> float:
    """Risk from a mismatch between physical and financial completion, in either direction."""
    mismatch = abs(physical_progress - expenditure_pct_of_revised_cost)
    return clamp(mismatch * FINANCIAL_RISK_SCALE)


def risk_score(
    delay_probability: float,
    cost_overrun_probability: float,
    progress_gap_pct: float,
    physical_progress: float,
    expenditure_pct_of_revised_cost: float,
) -> tuple[float, float, float]:
    """Returns (risk_score, progress_risk, financial_risk)."""
    p_risk = progress_risk(progress_gap_pct)
    f_risk = financial_risk(physical_progress, expenditure_pct_of_revised_cost)
    score = (
        DELAY_WEIGHT * delay_probability * 100
        + COST_WEIGHT * cost_overrun_probability * 100
        + PROGRESS_WEIGHT * p_risk
        + FINANCIAL_WEIGHT * f_risk
    )
    return clamp(score), p_risk, f_risk


def risk_level(score: float) -> str:
    if score > 80:
        return "critical"
    if score > 60:
        return "high"
    if score > 30:
        return "medium"
    return "low"


def confidence_from_probability(probability: float) -> float:
    """Heuristic confidence: how far the model's probability sits from a 50/50 guess."""
    return round(min(0.95, 0.55 + abs(probability - 0.5)), 2)
