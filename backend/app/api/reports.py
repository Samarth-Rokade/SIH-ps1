from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import DashboardReportRequest, ReportRequest
from app.services import report_service
from app.utils.response import ApiError, success

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports():
    return success([r.model_dump(mode="json") for r in report_service.list_reports()])


@router.post("/project/{project_id}")
def project_report(project_id: str, body: ReportRequest = Body(default_factory=ReportRequest), db: Session = Depends(get_db)):
    return success(report_service.generate_project_report(db, project_id).model_dump(mode="json"))


@router.post("/dashboard")
def dashboard_report(
    body: DashboardReportRequest = Body(default_factory=DashboardReportRequest), db: Session = Depends(get_db)
):
    return success(report_service.generate_dashboard_report(db, body.month).model_dump(mode="json"))


@router.get("/{report_id}/download")
def download(report_id: str):
    found = report_service.report_path(report_id)
    if found is None:
        raise ApiError(404, "REPORT_NOT_FOUND", f"Report {report_id} was not found")
    path, info = found
    return FileResponse(path, media_type="application/pdf", filename=f"{info.report_id}-{info.kind}-report.pdf")
