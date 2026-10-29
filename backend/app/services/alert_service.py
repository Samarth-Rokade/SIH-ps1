from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Alert, Project
from app.database.schemas import AlertDetail, AlertListItem, AlertSummary, AlertUpdateResult

RECOMMENDED_REVIEW = {
    "progress_stagnation": "Review upcoming milestone execution and contractor mobilisation.",
    "schedule_overrun": "Re-baseline the completion date and review the recovery plan with the executing agency.",
    "expenditure_divergence": "Reconcile expenditure against physical progress and review pending bills.",
    "milestone_risk": "Hold a milestone review and confirm resource availability for upcoming packages.",
    "general_risk": "Schedule a project review covering schedule, cost and progress indicators.",
}


def list_alerts(
    db: Session,
    page: int,
    page_size: int,
    severity: str | None,
    state: str | None,
    sector: str | None,
    status: str | None = None,
) -> tuple[list[AlertListItem], int]:
    query = db.query(Alert, Project).join(Project, Alert.project_id == Project.project_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if state:
        query = query.filter(Project.state == state)
    if sector:
        query = query.filter(Project.sector == sector)
    if status:
        query = query.filter(Alert.status == status)

    total = query.count()
    rows = (
        query.order_by(Alert.risk_current.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        AlertListItem(
            alert_id=alert.alert_id,
            project_id=alert.project_id,
            project_name=project.project_name,
            severity=alert.severity,
            risk_score=alert.risk_current,
            alert_type=alert.alert_type,
            message=alert.message,
            detected_at=alert.detected_at,
            status=alert.status,
        )
        for alert, project in rows
    ]
    return items, total


def get_summary(db: Session) -> AlertSummary:
    counts = {
        level: db.query(Alert).filter(Alert.severity == level).count()
        for level in ("critical", "high", "medium")
    }
    new_count = db.query(Alert).filter(Alert.status == "new").count()
    resolved_count = db.query(Alert).filter(Alert.status == "resolved").count()
    return AlertSummary(
        critical=counts["critical"],
        high=counts["high"],
        medium=counts["medium"],
        new=new_count,
        resolved=resolved_count,
    )


def get_alert(db: Session, alert_id: str) -> AlertDetail | None:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if alert is None:
        return None
    return AlertDetail(
        alert_id=alert.alert_id,
        project_id=alert.project_id,
        severity=alert.severity,
        type=alert.alert_type,
        title=alert.title,
        description=alert.message,
        detected_at=alert.detected_at,
        status=alert.status,
        risk_before=alert.risk_before,
        risk_current=alert.risk_current,
        recommended_review=RECOMMENDED_REVIEW.get(alert.alert_type, RECOMMENDED_REVIEW["general_risk"]),
    )


def update_status(db: Session, alert_id: str, status: str) -> AlertUpdateResult | None:
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if alert is None:
        return None
    alert.status = status
    db.commit()
    return AlertUpdateResult(alert_id=alert.alert_id, status=alert.status)
