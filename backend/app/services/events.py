from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import EmailEvent, EmailEventType, Lead, LeadStatus
from app.services.scoring import recompute_score
from app.services.suppression import suppress_email

_STATUS_FROM_EVENT_TYPE = {
    "sent": LeadStatus.SENT.value,
    "opened": LeadStatus.OPENED.value,
    "replied": LeadStatus.REPLIED.value,
    "unsubscribed": LeadStatus.UNSUBSCRIBED.value,
}


def record_event(
    db: Session,
    lead: Lead,
    event_type: str,
    event_metadata: Optional[dict] = None,
) -> EmailEvent:
    """Single place where an email event is recorded: writes the raw event,
    updates the lead's derived status, honours unsubscribes by adding the
    address to the suppression list, and recomputes the score. Used by the
    manual event API, the real send flow, and the public tracking routes."""
    event = EmailEvent(lead_id=lead.id, event_type=event_type, event_metadata=event_metadata)
    db.add(event)
    db.flush()

    new_status = _STATUS_FROM_EVENT_TYPE.get(event_type)
    if new_status is not None:
        lead.status = new_status

    if event_type == EmailEventType.UNSUBSCRIBED.value:
        suppress_email(db, lead.email, reason="unsubscribed")

    recompute_score(db, lead, triggered_by_event_id=event.id)
    return event