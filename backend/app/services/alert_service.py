from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Alert, Project
from app.database.schemas import AlertListItem, AlertSummary


def list_alerts(
    db: Session,
    page: int,
    page_size: int,
    severity: str | None,
    state: str | None,
    sector: str | None,
) -> tuple[list[AlertListItem], int]:
    query = db.query(Alert, Project).join(Project, Alert.project_id == Project.project_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if state:
        query = query.filter(Project.state == state)
    if sector:
        query = query.filter(Project.sector == sector)

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
