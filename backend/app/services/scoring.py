import json
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import EmailEvent, EmailEventType, Lead, Score, ScoreHistory

_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "config" / "scoring_weights.json"


def _load_weights() -> dict:
    with open(_WEIGHTS_PATH) as f:
        return json.load(f)


WEIGHTS = _load_weights()


def _compute_fit(lead: Lead) -> Tuple[int, List[str]]:
    cfg = WEIGHTS["fit"]
    icp = (lead.campaign.icp_criteria or {}) if lead.campaign else {}
    points = 0
    reasons: List[str] = []

    titles = [t.lower() for t in icp.get("titles", [])]
    if lead.title and titles and any(t in lead.title.lower() for t in titles):
        points += cfg["title_match_points"]
        reasons.append("title matches ICP")

    industry = icp.get("industry")
    if industry and lead.company and lead.company.industry and industry.lower() == lead.company.industry.lower():
        points += cfg["industry_match_points"]
        reasons.append("industry matches ICP")

    region = icp.get("region")
    if region and lead.company and lead.company.region and region.lower() == lead.company.region.lower():
        points += cfg["region_match_points"]
        reasons.append("region matches ICP")

    size = icp.get("company_size")
    if size and lead.company and lead.company.size and size.lower() == lead.company.size.lower():
        points += cfg["company_size_match_points"]
        reasons.append("company size matches ICP")

    return min(points, cfg["max_fit_score"]), reasons


def _compute_engagement(db: Session, lead_id: int) -> Tuple[int, bool, List[str]]:
    cfg = WEIGHTS["engagement"]
    event_points = cfg["event_points"]

    seen_types = set(
        db.execute(select(EmailEvent.event_type).where(EmailEvent.lead_id == lead_id)).scalars().all()
    )

    best_points = 0
    best_type: Optional[str] = None
    for event_type in seen_types:
        pts = event_points.get(event_type, 0)
        if pts > best_points:
            best_points = pts
            best_type = event_type

    unsubscribed = EmailEventType.UNSUBSCRIBED.value in seen_types
    reasons = [f"engagement based on '{best_type}' event"] if best_type else []
    return min(best_points, cfg["max_engagement_score"]), unsubscribed, reasons


def recompute_score(
    db: Session,
    lead: Lead,
    triggered_by_event_id: Optional[int] = None,
) -> Score:
    """Recompute a lead's score from scratch (fit + engagement) and append
    a score_history row explaining the change. Called on lead creation and
    on every email event."""
    fit_points, fit_reasons = _compute_fit(lead)
    engagement_points, unsubscribed, engagement_reasons = _compute_engagement(db, lead.id)

    raw_total = fit_points + engagement_points
    reasons = fit_reasons + engagement_reasons
    if unsubscribed:
        raw_total = min(raw_total, WEIGHTS["unsubscribed_score_cap"])
        reasons.append("capped: lead unsubscribed")

    new_value = max(0, min(100, raw_total))

    score = lead.score
    old_value = score.value if score else None

    if score is None:
        score = Score(
            lead_id=lead.id,
            value=new_value,
            fit_component=fit_points,
            engagement_component=engagement_points,
        )
        db.add(score)
    else:
        score.value = new_value
        score.fit_component = fit_points
        score.engagement_component = engagement_points

    db.add(
        ScoreHistory(
            lead_id=lead.id,
            triggered_by_event_id=triggered_by_event_id,
            old_score=old_value,
            new_score=new_value,
            reason="; ".join(reasons) if reasons else "no ICP or engagement signals yet",
        )
    )

    return score