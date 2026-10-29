"""PDF report generation (API spec S34-36).

Reports are rendered with reportlab, saved under backend/reports/ as
`R<id>.pdf` with a small `R<id>.json` metadata sidecar (so the report list and
downloads survive server restarts), and served by id.
"""
from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.database.models import Alert
from app.database.schemas import ReportInfo
from app.services import analytics_service, dashboard_service, history_service, project_service
from app.utils.constants import DATA_AS_OF
from app.utils.response import ApiError

REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"
FIRST_REPORT_NUMBER = 1001
REPORT_ID_RE = re.compile(r"^R\d{4,}$")
LIST_LIMIT = 20
DISCLAIMER = (
    "Model-generated decision-support output based on a monthly PAIMANA data snapshot. "
    "Predictions are estimates, not guaranteed outcomes."
)
ACCENT = colors.HexColor("#3b5b8a")
LEVEL_COLORS = {
    "critical": colors.HexColor("#ef4444"),
    "high": colors.HexColor("#f97316"),
    "medium": colors.HexColor("#ca8a04"),
    "low": colors.HexColor("#16a34a"),
}

_lock = threading.Lock()
_styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_styles["Heading1"], textColor=ACCENT, fontSize=18, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=_styles["Heading2"], textColor=ACCENT, fontSize=12, spaceBefore=12, spaceAfter=4)
BODY = ParagraphStyle("Body", parent=_styles["BodyText"], fontSize=9, leading=12)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=7.5, textColor=colors.grey)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=8, leading=10)


def _next_report_id() -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    numbers = [int(p.stem[1:]) for p in REPORT_DIR.glob("R*.pdf") if REPORT_ID_RE.match(p.stem)]
    return f"R{max(numbers, default=FIRST_REPORT_NUMBER - 1) + 1}"


def _table(rows: list[list], col_widths: list[float] | None = None, header: bool = True) -> Table:
    wrapped = [[Paragraph(str(c), CELL) for c in row] for row in rows]
    table = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9dcee")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e1ebf6"))]
    table.setStyle(TableStyle(style))
    return table


def _cr(value: float) -> str:
    return f"Rs {value:,.1f} Cr"


def _level(level: str) -> str:
    return f'<font color="{LEVEL_COLORS[level].hexval().replace("0x", "#")}"><b>{level.upper()}</b></font>'


def _build_pdf(path: Path, title: str, story: list) -> None:
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(15 * mm, 10 * mm, "PAIMANA Sentinel AI  |  " + title)
        canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(path), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=18 * mm,
        title=title, author="PAIMANA Sentinel AI",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def _save(kind: str, title: str, story: list) -> ReportInfo:
    with _lock:
        report_id = _next_report_id()
        _build_pdf(REPORT_DIR / f"{report_id}.pdf", title, story)
        info = ReportInfo(
            report_id=report_id,
            kind=kind,
            title=title,
            status="generated",
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            download_url=f"/api/v1/reports/{report_id}/download",
        )
        (REPORT_DIR / f"{report_id}.json").write_text(info.model_dump_json())
    return info


def generate_project_report(db: Session, project_id: str) -> ReportInfo:
    project = project_service.get_project(db, project_id)
    if project is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", f"Project with ID {project_id} was not found")
    risk = project_service.get_risk(db, project_id)
    delay = project_service.get_delay_prediction(db, project_id)
    cost = project_service.get_cost_prediction(db, project_id)
    drivers = project_service.get_risk_drivers(db, project_id)
    benchmark = history_service.get_benchmark(db, project_id)
    timeline = history_service.get_timeline(db, project_id)
    alerts = db.query(Alert).filter(Alert.project_id == project_id).all()

    story: list = [
        Paragraph("Project Risk Report", H1),
        Paragraph(project.project_name, ParagraphStyle("Name", parent=BODY, fontSize=11, leading=14)),
        Paragraph(
            f"{project.project_id} &nbsp;|&nbsp; {project.ministry} &nbsp;|&nbsp; {project.sector} &nbsp;|&nbsp; "
            f"{project.state} &nbsp;|&nbsp; Data as of {DATA_AS_OF:%d %b %Y}",
            SMALL,
        ),
        Paragraph("Risk Assessment", H2),
        _table(
            [
                ["Overall risk", f"{risk.risk_score:g} / 100 &nbsp;{_level(risk.risk_level)}", "Confidence", f"{risk.confidence:.0%}"],
                ["Delay probability", f"{risk.delay_probability:.0%}", "Cost-overrun probability", f"{risk.cost_overrun_probability:.0%}"],
                ["Progress risk", f"{risk.progress_risk:.0f}", "Financial risk", f"{risk.financial_risk:.0f}"],
            ],
            header=False,
        ),
        Paragraph("Delay Prediction", H2),
        _table(
            [
                ["Estimated delay", f"{delay.predicted_delay_months} months", "Likely range",
                 f"{delay.prediction_range.lower}-{delay.prediction_range.upper} months"],
                ["Start date", f"{project.start_date:%d %b %Y}", "Planned completion", f"{project.original_completion_date:%d %b %Y}"],
                ["Predicted completion", f"{timeline.predicted_end_date:%d %b %Y}", "Model", delay.model],
            ],
            header=False,
        ),
        Paragraph("Cost Forecast", H2),
        _table(
            [
                ["Original cost", _cr(cost.original_cost_crore), "Current cost", _cr(cost.current_cost_crore)],
                ["Predicted final cost", _cr(cost.predicted_final_cost_crore), "Expected escalation", f"{cost.expected_escalation_percentage:g}%"],
                ["Additional exposure", _cr(cost.additional_exposure_crore), "Expenditure to date", _cr(project.expenditure_crore)],
                ["Physical progress", f"{project.physical_progress:g}%", "Status", project.status],
            ],
            header=False,
        ),
        Paragraph("Key Risk Drivers (SHAP)", H2),
        _table(
            [["Driver", "Value", "Effect", "Impact (pts)"]]
            + [
                [d.feature, f"{d.value:g}", "Raises risk" if d.direction == "increases" else "Lowers risk", f"{d.impact:g}"]
                for d in drivers.drivers
            ],
            [70 * mm, 30 * mm, 40 * mm, 30 * mm],
        ),
    ]
    peers = benchmark.similar_projects
    story += [
        Paragraph("Peer Benchmark", H2),
        Paragraph(f"Compared with {peers.count} similar projects ({peers.basis}).", BODY),
        _table(
            [
                ["Metric", "This project", "Peer average", "Difference"],
                ["Risk score", f"{benchmark.project.risk:g}", f"{peers.average_risk:g}", f"{benchmark.comparison.risk_difference:+g}"],
                ["Physical progress (%)", f"{benchmark.project.progress:g}", f"{peers.average_progress:g}", f"{benchmark.comparison.progress_difference:+g}"],
                ["Expenditure (% of cost)", f"{benchmark.project.expenditure_percentage:g}", f"{peers.average_expenditure_percentage:g}",
                 f"{benchmark.comparison.expenditure_difference:+g}"],
            ],
            [60 * mm, 40 * mm, 40 * mm, 30 * mm],
        ),
    ]
    if alerts:
        story += [
            Paragraph("Early-Warning Alerts", H2),
            _table(
                [["Alert", "Severity", "Status", "Detail"]]
                + [[a.alert_id, _level(a.severity), a.status, a.message] for a in alerts],
                [25 * mm, 25 * mm, 30 * mm, 90 * mm],
            ),
        ]
    story += [Spacer(1, 10), Paragraph(DISCLAIMER, SMALL)]
    return _save("project", f"Project Report - {project.project_name[:70]}", story)


def generate_dashboard_report(db: Session, month: str | None) -> ReportInfo:
    overview = dashboard_service.get_overview(db)
    distribution = dashboard_service.get_risk_distribution(db)
    priority = dashboard_service.get_priority_projects(db, 10)
    ministries = analytics_service.get_ministries(db)
    sectors = analytics_service.get_sectors(db)
    cost = analytics_service.get_cost(db, None, None, None)

    label = month or f"{DATA_AS_OF:%Y-%m}"
    story: list = [
        Paragraph("Portfolio Risk Report", H1),
        Paragraph(f"Reporting period {label} &nbsp;|&nbsp; Data as of {overview.data_as_of:%d %b %Y}", SMALL),
        Paragraph("Key Indicators", H2),
        _table(
            [
                ["Monitored projects", f"{overview.total_projects:,}", "Need intervention", f"{overview.projects_needing_intervention:,}"],
                ["Critical", f"{overview.critical_projects:,}", "High", f"{overview.high_risk_projects:,}"],
                ["Average delay risk", f"{overview.average_delay_risk:g}%", "Forecast cost exposure", _cr(overview.cost_exposure_crore)],
                ["Original cost", _cr(cost.total_original_cost_crore), "Current cost", _cr(cost.total_current_cost_crore)],
            ],
            header=False,
        ),
        Paragraph("Risk Distribution", H2),
        _table(
            [["Level", "Projects", "Share"]]
            + [[_level(b.level), f"{b.count:,}", f"{b.percentage:g}%"] for b in distribution.distribution],
            [50 * mm, 40 * mm, 40 * mm],
        ),
        Paragraph("Top 10 Priority Projects", H2),
        _table(
            [["Project", "Ministry", "Risk", "Level", "Est. delay"]]
            + [
                [p.project_name[:80], p.ministry[:40], f"{p.risk_score:g}", _level(p.risk_level), f"{p.predicted_delay_months} mo"]
                for p in priority
            ],
            [70 * mm, 45 * mm, 15 * mm, 22 * mm, 22 * mm],
        ),
        Paragraph("Ministry Benchmarking", H2),
        _table(
            [["Ministry", "Projects", "Avg risk", "High/critical %", "Avg delay (mo)", "Cost escalation %"]]
            + [
                [m.ministry[:50], m.projects, f"{m.average_risk:g}", f"{m.high_risk_percentage:g}", f"{m.average_delay_months:g}",
                 f"{m.cost_escalation_percentage:g}"]
                for m in ministries
            ],
            [60 * mm, 18 * mm, 18 * mm, 25 * mm, 25 * mm, 28 * mm],
        ),
        Paragraph("Sector Analytics", H2),
        _table(
            [["Sector", "Projects", "Avg risk", "High/critical %"]]
            + [[s.sector, s.projects, f"{s.average_risk:g}", f"{s.high_risk_percentage:g}"] for s in sectors],
            [80 * mm, 25 * mm, 25 * mm, 30 * mm],
        ),
        Spacer(1, 10),
        Paragraph(DISCLAIMER, SMALL),
    ]
    return _save("dashboard", f"Portfolio Report - {label}", story)


def _load_info(report_id: str) -> ReportInfo | None:
    if not REPORT_ID_RE.match(report_id):
        return None
    meta = REPORT_DIR / f"{report_id}.json"
    if not meta.exists() or not (REPORT_DIR / f"{report_id}.pdf").exists():
        return None
    return ReportInfo.model_validate_json(meta.read_text())


def report_path(report_id: str) -> tuple[Path, ReportInfo] | None:
    info = _load_info(report_id)
    return (REPORT_DIR / f"{report_id}.pdf", info) if info else None


def list_reports() -> list[ReportInfo]:
    if not REPORT_DIR.exists():
        return []
    infos = [info for p in REPORT_DIR.glob("R*.json") if (info := _load_info(p.stem))]
    return sorted(infos, key=lambda i: int(i.report_id[1:]), reverse=True)[:LIST_LIMIT]
