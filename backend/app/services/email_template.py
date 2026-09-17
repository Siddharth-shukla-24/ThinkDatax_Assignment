import logging
from typing import Optional

from app.core.config import settings
from app.db.models import Company, Lead

logger = logging.getLogger("app.grounding")

COMPANY_SEGMENT = "apparel and fashion brands and retailers"


def _get(source: dict, key: str, dropped: list) -> Optional[str]:
    value = source.get(key)
    if not value:
        dropped.append(key)
        return None
    return value


def render_email(lead: Lead, company: Company) -> dict:
    """Fill the Appendix A skeleton using only values stored on the lead or
    company (or their raw_data research fields). Any bracketed sentence whose
    token isn't grounded in stored data is dropped, never invented, and every
    drop is logged for the grounding check."""
    lead_data = lead.raw_data or {}
    company_data = company.raw_data or {}
    dropped: list = []

    observed_signal_sentence = _get(lead_data, "observed_signal_sentence", dropped)
    observed_signal_short = _get(lead_data, "observed_signal_short", dropped)
    pain_point_category = _get(company_data, "pain_point_category", dropped)
    value_prop_for_pain_point = _get(company_data, "value_prop_for_pain_point", dropped)
    specific_context_detail = _get(company_data, "specific_context_detail", dropped)
    one_line_relevance_hypothesis = _get(lead_data, "one_line_relevance_hypothesis", dropped)
    # optional tokens: fine to omit silently, not part of the grounding check
    quantified_outcome_optional = lead_data.get("quantified_outcome_optional")
    proposed_time_window = lead_data.get("proposed_time_window")
    optional_soft_proof_point = lead_data.get("optional_soft_proof_point")

    if observed_signal_short:
        subject = f"{company.name}'s {observed_signal_short} - quick question"
    elif pain_point_category:
        subject = f"Cutting {pain_point_category} at {company.name}"
    else:
        subject = f"Quick question for {company.name}"
        dropped.append("subject_signal_or_pain")

    lines = [f"Hi {lead.first_name},", ""]

    if observed_signal_sentence:
        lines += [f"I noticed {observed_signal_sentence}.", ""]

    if value_prop_for_pain_point:
        outcome = f" - {quantified_outcome_optional}" if quantified_outcome_optional else ""
        lines += [
            f"At StyleSense AI, we help {COMPANY_SEGMENT} teams "
            f"{value_prop_for_pain_point}{outcome}.",
            "",
        ]

    if specific_context_detail and one_line_relevance_hypothesis:
        lines += [
            f"Given {company.name}'s {specific_context_detail}, {one_line_relevance_hypothesis}.",
            "",
        ]

    time_window = f" {proposed_time_window}" if proposed_time_window else ""
    lines += [
        f"Would you be open to a 15-minute call{time_window} to see if it's a fit?",
        "",
        "Best,",
        settings.sender_name,
        "StyleSense AI",
    ]

    if optional_soft_proof_point:
        lines += ["", f"P.S. {optional_soft_proof_point}"]

    if dropped:
        logger.info(
            "Grounding check dropped ungrounded tokens for lead_id=%s: %s", lead.id, dropped
        )

    return {"subject": subject, "body": "\n".join(lines), "dropped_tokens": dropped}


def to_html(body_text: str, tracking_pixel_url: str, unsubscribe_url: str) -> str:
    escaped = body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_body = escaped.replace("\n", "<br>")
    footer = (
        f'<hr><p style="font-size:12px;color:#666;">'
        f'If you\'d prefer not to hear from us again, '
        f'<a href="{unsubscribe_url}">unsubscribe here</a>.</p>'
        f'<img src="{tracking_pixel_url}" width="1" height="1" style="display:none" alt="">'
    )
    return f'<div style="font-family:sans-serif;">{html_body}</div>{footer}'