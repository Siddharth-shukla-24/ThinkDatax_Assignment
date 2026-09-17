from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import EmailEvent, EmailEventType, Lead
from app.schemas.event import EventRead
from app.services.email_provider import send_email
from app.services.email_template import render_email, to_html
from app.services.events import record_event
from app.services.suppression import is_suppressed
from app.services.tokens import make_unsubscribe_token

router = APIRouter(prefix="/leads", tags=["email"], dependencies=[Depends(require_api_token)])


@router.post("/{lead_id}/send", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def send_lead_email(lead_id: int, db: Session = Depends(get_db)) -> EmailEvent:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    if is_suppressed(db, lead.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This email address is on the suppression list and will not be sent to.",
        )

    rendered = render_email(lead, lead.company)
    unsubscribe_url = f"{settings.app_base_url}/unsubscribe/{make_unsubscribe_token(lead.id)}"
    pixel_url = f"{settings.app_base_url}/track/pixel/{lead.id}"
    html = to_html(rendered["body"], tracking_pixel_url=pixel_url, unsubscribe_url=unsubscribe_url)

    provider_result = send_email(
        to=lead.email, subject=rendered["subject"], html=html, text=rendered["body"]
    )

    event = record_event(
        db,
        lead,
        EmailEventType.SENT.value,
        event_metadata={
            "subject": rendered["subject"],
            "dropped_tokens": rendered["dropped_tokens"],
            "provider_id": provider_result.get("id"),
            "mocked": provider_result.get("mocked", False),
            "unsubscribe_url": unsubscribe_url,
        },
    )
    event_id = event.id
    db.commit()

    saved_event = db.get(EmailEvent, event_id)
    if saved_event is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email event failed to persist.",
        )
    return saved_event