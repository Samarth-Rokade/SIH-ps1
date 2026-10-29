"""AI assistant: intent detection -> database retrieval -> grounded answer.

Pipeline (API spec S32): the question is classified, the relevant facts are
pulled from SQLite/analytics, and a deterministic answer is built from those
facts only. When a local Ollama model is available it re-phrases the answer
from the same facts (never from its own knowledge); otherwise the deterministic
answer is returned as-is. Either way no project statistic is invented.
"""
from __future__ import annotations

import re
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import lru_cache

from sqlalchemy.orm import Session

from app.database.models import Alert, Project, ProjectPrediction
from app.database.schemas import AssistantResponse, AssistantSource
from app.services import alert_service, analytics_service, dashboard_service, llm_client, project_service
from app.utils.state_coordinates import STATE_CENTROIDS

SUGGESTIONS = [
    "Which projects need immediate intervention?",
    "Which ministry has the highest risk?",
    "Which ministry has the highest delays?",
    "Show critical projects in Maharashtra.",
    "Which projects have high cost escalation?",
    "Which sector is riskiest?",
    "Give me an overview of the portfolio.",
]

SYSTEM_PROMPT = (
    "You are the PAIMANA Sentinel AI assistant for Indian infrastructure project monitoring. "
    "Answer the user's question using ONLY the FACTS provided. Never invent projects, numbers or "
    "causes. If the facts do not contain the answer, say you do not have that data. "
    "Be concise (under 130 words), plain and specific; keep project names and numbers exactly as given."
)

STOPWORDS = {
    "why", "is", "are", "the", "a", "an", "of", "in", "on", "for", "to", "me", "show", "list", "which", "what",
    "who", "how", "many", "much", "has", "have", "highest", "most", "risk", "risky", "high", "critical", "delay",
    "delayed", "delays", "project", "projects", "cost", "this", "that", "it", "and", "or", "with", "about",
    "explain", "tell", "give", "any", "all", "there", "does", "do", "be", "at", "by", "from", "need", "needs",
    "immediate", "intervention", "priority", "escalation", "overrun", "overruns", "ministry", "sector", "state",
    "worst", "top", "currently", "right", "now", "please", "can", "you", "whats", "status",
}
GENERIC_NAME_WORDS = {"ministry", "department", "of", "and", "for", "the"}
NON_STATE_LABELS = {"Multi-States", "PAN India", "Offshore"}
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PROJECT_ID_RE = re.compile(r"\bP\d{5}\b", re.IGNORECASE)
LIST_LIMIT = 5
MAX_CONVERSATIONS = 200
MIN_NAME_MATCH_SCORE = 0.6
MIN_SECTOR_PEERS = 5  # minimum projects for a ministry/sector/state to appear in a ranking

_conversations: "OrderedDict[str, dict]" = OrderedDict()


@dataclass
class Answer:
    text: str
    facts: str
    sources: list[AssistantSource] = field(default_factory=list)
    project_id: str | None = None


def _tokens(text: str) -> set[str]:
    found: set[str] = set()
    for tok in TOKEN_RE.findall(text.lower()):
        found.add(tok)
        found.update(part for part in tok.split("-") if part)
    return found


@lru_cache(maxsize=1)
def _name_index() -> tuple[tuple[str, frozenset[str]], ...]:
    from app.database.database import SessionLocal

    with SessionLocal() as db:
        rows = db.query(Project.project_id, Project.project_name).all()
    return tuple((pid, frozenset(_tokens(name))) for pid, name in rows)


def _distinct(db: Session, column) -> list[str]:
    return [v for (v,) in db.query(column).distinct().all()]


@lru_cache(maxsize=1)
def _entity_words_cached(sectors: tuple[str, ...], ministries: tuple[str, ...]) -> frozenset[str]:
    words: set[str] = set()
    for name in [*STATE_CENTROIDS, *sectors, *ministries]:
        words |= _tokens(name)
    return frozenset(words)


def _entity_words(db: Session) -> frozenset[str]:
    return _entity_words_cached(tuple(_distinct(db, Project.sector)), tuple(_distinct(db, Project.ministry)))


def _find_project(db: Session, message: str) -> str | None:
    match = PROJECT_ID_RE.search(message)
    if match:
        pid = match.group(0).upper()
        if db.query(Project.project_id).filter(Project.project_id == pid).first():
            return pid
    content = {t for t in _tokens(message) if t not in STOPWORDS and (len(t) >= 3 or any(c.isdigit() for c in t))}
    # Words that name a state/sector/ministry describe a filter, not a project.
    content -= _entity_words(db)
    if len(content) < 2:
        return None
    best_pid, best_key = None, (0.0, 0)
    for pid, name_tokens in _name_index():
        hits = len(content & name_tokens)
        if hits < 2:
            continue
        key = (hits / len(content), hits)
        if key > best_key:
            best_pid, best_key = pid, key
    return best_pid if best_key[0] >= MIN_NAME_MATCH_SCORE else None


def _same_word(message_token: str, name_token: str) -> bool:
    """Plural/singular-tolerant word match ('railway' ~ 'railways') without loose prefixes ('intervention' !~ 'internal')."""
    if len(message_token) < 4:
        return False
    return message_token.startswith(name_token[:6]) or (len(message_token) >= 5 and name_token.startswith(message_token))


def _match_entity(message: str, names: list[str]) -> str | None:
    """Picks the name whose words best overlap the message (prefix-tolerant: 'railway' ~ 'Railways')."""
    msg_tokens = _tokens(message)
    best, best_score = None, 0
    for name in names:
        name_tokens = {t for t in _tokens(name) if t not in GENERIC_NAME_WORDS and len(t) > 3}
        score = sum(1 for nt in name_tokens if any(_same_word(mt, nt) for mt in msg_tokens))
        if score > best_score:
            best, best_score = name, score
    return best


def _match_state(message: str) -> str | None:
    lowered = message.lower()
    for state in sorted((s for s in STATE_CENTROIDS if s not in NON_STATE_LABELS), key=len, reverse=True):
        if state.lower() in lowered:
            return state
    return None


def _project_rows(db: Session, level, state, sector, ministry, order, limit: int):
    query = db.query(Project, ProjectPrediction).join(ProjectPrediction, Project.project_id == ProjectPrediction.project_id)
    if level:
        query = query.filter(ProjectPrediction.risk_level.in_(level))
    if state:
        query = query.filter(Project.state == state)
    if sector:
        query = query.filter(Project.sector == sector)
    if ministry:
        query = query.filter(Project.ministry == ministry)
    total = query.count()
    return query.order_by(order.desc()).limit(limit).all(), total


def _scope_label(state, sector, ministry) -> str:
    parts = [p for p in (state and f"in {state}", sector and f"in the {sector} sector", ministry and f"under {ministry}") if p]
    return (" " + " ".join(parts)) if parts else ""


def _sources(rows) -> list[AssistantSource]:
    return [AssistantSource(project_id=p.project_id, project_name=p.project_name) for p, _ in rows]


def _answer_project(db: Session, project_id: str) -> Answer:
    project = project_service.get_project(db, project_id)
    risk = project_service.get_risk(db, project_id)
    delay = project_service.get_delay_prediction(db, project_id)
    cost = project_service.get_cost_prediction(db, project_id)
    drivers = project_service.get_risk_drivers(db, project_id)
    raw = db.query(Project).filter(Project.project_id == project_id).first()
    alerts = db.query(Alert).filter(Alert.project_id == project_id).count()

    driver_text = "; ".join(
        f"{d.feature} {'raises' if d.direction == 'increases' else 'lowers'} risk by {d.impact:g} pts (value {d.value:g})"
        for d in drivers.drivers[:4]
    )
    facts = "\n".join(
        [
            f"{project.project_name} ({project_id}) - {project.ministry}, {project.sector}, {project.state}.",
            f"Risk score {risk.risk_score:g} ({risk.risk_level}); delay probability {round(risk.delay_probability * 100)}%, "
            f"cost-overrun probability {round(risk.cost_overrun_probability * 100)}%.",
            f"Physical progress {project.physical_progress:g}% vs {raw.time_elapsed_pct:g}% of planned time elapsed "
            f"(progress gap {raw.progress_gap_pct:g} pts); expenditure is {raw.expenditure_pct_of_revised_cost:g}% of revised cost.",
            f"Estimated delay {delay.predicted_delay_months} months (range {delay.prediction_range.lower}-{delay.prediction_range.upper}).",
            f"Cost: original Rs {cost.original_cost_crore:,.1f} Cr, current Rs {cost.current_cost_crore:,.1f} Cr, "
            f"predicted final Rs {cost.predicted_final_cost_crore:,.1f} Cr (additional exposure Rs {cost.additional_exposure_crore:,.1f} Cr).",
            f"Top risk drivers: {driver_text or 'not available'}.",
            f"Early-warning alerts raised: {alerts}.",
        ]
    )
    text = (
        f"{project.project_name} is rated {risk.risk_level.upper()} risk (score {risk.risk_score:g}). "
        f"Progress is {project.physical_progress:g}% against {raw.time_elapsed_pct:g}% of planned time elapsed, with a "
        f"delay probability of {round(risk.delay_probability * 100)}% and an estimated delay of "
        f"{delay.predicted_delay_months} months. "
        + (f"The main drivers are: {driver_text}. " if driver_text else "")
        + f"Cost is forecast at Rs {cost.predicted_final_cost_crore:,.1f} Cr against Rs {cost.original_cost_crore:,.1f} Cr originally sanctioned."
    )
    return Answer(text, facts, [AssistantSource(project_id=project_id, project_name=project.project_name)], project_id)


def _answer_priority(db: Session, level: list[str], state, sector, ministry, label: str) -> Answer:
    rows, total = _project_rows(db, level, state, sector, ministry, ProjectPrediction.risk_score, LIST_LIMIT)
    scope = _scope_label(state, sector, ministry)
    if not rows:
        text = f"No {label} projects were found{scope}."
        return Answer(text, text)
    listing = "; ".join(
        f"{p.project_name} (risk {pr.risk_score:g}, est. delay {pr.predicted_delay_months} mo, {p.state})" for p, pr in rows
    )
    text = f"There are {total} {label} projects{scope}. The highest-risk ones are: {listing}."
    return Answer(text, text, _sources(rows))


def _answer_ministry(db: Session, by: str) -> Answer:
    keys = {
        "delay": lambda m: m.average_delay_months,
        "cost": lambda m: m.cost_escalation_percentage,
        "risk": lambda m: m.average_risk,
    }
    ministries = analytics_service.get_ministries(db)
    # Ignore ministries with a handful of projects so one outlier can't top a ranking.
    rows = sorted([m for m in ministries if m.projects >= MIN_SECTOR_PEERS] or ministries, key=keys[by], reverse=True)
    metric = {"delay": "average predicted delay", "cost": "cost escalation", "risk": "average risk"}[by]
    top = rows[:3]

    def describe(m) -> str:
        return (
            f"{m.ministry} (avg risk {m.average_risk:g}, avg delay {m.average_delay_months:g} mo, "
            f"cost escalation {m.cost_escalation_percentage:g}%, {m.projects} projects)"
        )

    text = f"By {metric}, the top ministry is {describe(top[0])}. Next: " + "; ".join(describe(m) for m in top[1:]) + "."
    return Answer(text, text)


def _answer_sector(db: Session) -> Answer:
    rows = analytics_service.get_sectors(db)
    top = [s for s in rows if s.projects >= MIN_SECTOR_PEERS][:3] or rows[:3]
    text = f"Riskiest sectors by average risk score (sectors with {MIN_SECTOR_PEERS}+ projects): " + "; ".join(
        f"{s.sector} (avg risk {s.average_risk:g}, {s.high_risk_percentage:g}% high/critical, {s.projects} projects)" for s in top
    ) + "."
    return Answer(text, text)


def _answer_state(db: Session) -> Answer:
    rows = analytics_service.get_states(db)
    top = [s for s in rows if s.projects >= MIN_SECTOR_PEERS][:3] or rows[:3]
    text = f"States with the highest average risk ({MIN_SECTOR_PEERS}+ projects): " + "; ".join(
        f"{s.state} (avg risk {s.average_risk:g}, {s.critical_projects} critical of {s.projects})" for s in top
    ) + "."
    return Answer(text, text)


def _answer_cost(db: Session, sector, ministry) -> Answer:
    cost = analytics_service.get_cost(db, sector, ministry, None)
    top = cost.top_exposure_projects[:LIST_LIMIT]
    listing = "; ".join(
        f"{p.project_name} (+Rs {p.additional_exposure_crore:,.1f} Cr, predicted Rs {p.predicted_final_cost_crore:,.1f} Cr)" for p in top
    )
    text = (
        f"Across the {'filtered ' if sector or ministry else ''}portfolio, original cost is Rs {cost.total_original_cost_crore:,.0f} Cr "
        f"versus Rs {cost.total_current_cost_crore:,.0f} Cr currently (average realized escalation {cost.average_escalation_percentage:g}%; "
        f"{cost.projects_with_escalation} projects escalated). Highest forecast additional exposure: {listing}."
    )
    return Answer(text, text, [AssistantSource(project_id=p.project_id, project_name=p.project_name) for p in top])


def _answer_alerts(db: Session) -> Answer:
    s = alert_service.get_summary(db)
    text = (
        f"There are {s.critical + s.high + s.medium} early-warning alerts: {s.critical} critical, {s.high} high, "
        f"{s.medium} medium ({s.new} new, {s.resolved} resolved)."
    )
    return Answer(text, text)


def _answer_overview(db: Session) -> Answer:
    o = dashboard_service.get_overview(db)
    text = (
        f"The portfolio has {o.total_projects} monitored projects as of {o.data_as_of}: {o.critical_projects} critical, "
        f"{o.high_risk_projects} high, {o.medium_risk_projects} medium and {o.low_risk_projects} low risk. "
        f"{o.projects_needing_intervention} need intervention, average delay probability is {o.average_delay_risk:g}% and "
        f"forecast additional cost exposure is Rs {o.cost_exposure_crore:,.0f} Cr."
    )
    return Answer(text, text)


def _build_answer(db: Session, message: str, focus_project: str | None) -> Answer:
    lowered = message.lower()
    state = _match_state(message)
    sector = _match_entity(message, _distinct(db, Project.sector))
    ministry = _match_entity(message, _distinct(db, Project.ministry))
    wants_ministry = "ministr" in lowered or "department" in lowered
    is_list_question = re.search(r"\b(which|how many|show|list)\b", lowered) is not None

    project_id = _find_project(db, message)
    if project_id is None and focus_project and re.search(r"\b(it|this|that|its)\b", lowered):
        project_id = focus_project
    if project_id and not (is_list_question and re.search(r"\bprojects\b", lowered)):
        return _answer_project(db, project_id)

    if "alert" in lowered or "warning" in lowered:
        return _answer_alerts(db)
    if wants_ministry and re.search(r"delay|late|slow", lowered):
        return _answer_ministry(db, "delay")
    if wants_ministry and re.search(r"cost|escalat|overrun", lowered):
        return _answer_ministry(db, "cost")
    if wants_ministry:
        return _answer_ministry(db, "risk")
    if re.search(r"\bstates?\b", lowered) and re.search(r"which|highest|most|worst|rank", lowered) and not state:
        return _answer_state(db)
    if re.search(r"\bsectors?\b", lowered) and re.search(r"which|highest|most|worst|rank|riskiest", lowered) and not sector:
        return _answer_sector(db)
    if re.search(r"cost|escalat|overrun|exposure|budget", lowered):
        return _answer_cost(db, sector, ministry)
    if re.search(r"intervention|immediate|urgent|critical", lowered):
        return _answer_priority(db, ["critical"], state, sector, ministry, "critical")
    if re.search(r"high.?risk|risky|riskiest|priority|worst|top", lowered):
        return _answer_priority(db, ["critical", "high"], state, sector, ministry, "critical or high-risk")
    if re.search(r"delay|late|overdue|behind", lowered):
        rows, _ = _project_rows(db, None, state, sector, ministry, ProjectPrediction.predicted_delay_months, LIST_LIMIT)
        listing = "; ".join(f"{p.project_name} ({pr.predicted_delay_months} months)" for p, pr in rows)
        text = f"The projects with the longest predicted delays{_scope_label(state, sector, ministry)} are: {listing}."
        return Answer(text, text, _sources(rows))
    if re.search(r"overview|summary|portfolio|how many|total|status", lowered):
        return _answer_overview(db)
    if state or sector or ministry:
        return _answer_priority(db, ["critical", "high"], state, sector, ministry, "critical or high-risk")

    text = (
        "I can answer questions about project risk, delays, cost escalation, alerts, and ministry, sector or state "
        "comparisons using the monitored project data. Try one of the suggested questions, or ask about a project by name."
    )
    return Answer(text, text)


def _conversation_project(conversation_id: str) -> str | None:
    state = _conversations.get(conversation_id)
    return state["project_id"] if state else None


def _remember(conversation_id: str, project_id: str | None) -> None:
    state = _conversations.setdefault(conversation_id, {"project_id": None})
    _conversations.move_to_end(conversation_id)
    if project_id:
        state["project_id"] = project_id
    while len(_conversations) > MAX_CONVERSATIONS:
        _conversations.popitem(last=False)


def chat(db: Session, message: str, conversation_id: str | None, focus_project: str | None = None) -> AssistantResponse:
    conversation_id = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
    answer = _build_answer(db, message, focus_project or _conversation_project(conversation_id))
    _remember(conversation_id, answer.project_id)

    engine = "rule-based"
    reply = llm_client.generate(SYSTEM_PROMPT, f"FACTS:\n{answer.facts}\n\nQUESTION: {message}")
    if reply:
        answer.text, engine = reply, f"ollama:{llm_client.model_name()}"
    return AssistantResponse(conversation_id=conversation_id, answer=answer.text, sources=answer.sources, engine=engine)
