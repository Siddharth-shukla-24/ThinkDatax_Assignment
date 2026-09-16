from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import EmailEvent, Lead, LeadStatus
from app.schemas.event import EventCreate, EventRead
from app.services.scoring import recompute_score

router = APIRouter(
    prefix="/leads/{lead_id}/events", tags=["events"], dependencies=[Depends(require_api_token)]
)

_STATUS_FROM_EVENT_TYPE = {
    "sent": LeadStatus.SENT.value,
    "opened": LeadStatus.OPENED.value,
    "replied": LeadStatus.REPLIED.value,
    "unsubscribed": LeadStatus.UNSUBSCRIBED.value,
}


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(lead_id: int, payload: EventCreate, db: Session = Depends(get_db)) -> EmailEvent:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    event = EmailEvent(lead_id=lead_id, **payload.model_dump())
    db.add(event)
    db.flush()

    new_status = _STATUS_FROM_EVENT_TYPE.get(payload.event_type)
    if new_status is not None:
        lead.status = new_status

    recompute_score(db, lead, triggered_by_event_id=event.id)

    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=List[EventRead])
def list_events(lead_id: int, db: Session = Depends(get_db)) -> List[EmailEvent]:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")
    return (
        db.execute(select(EmailEvent).where(EmailEvent.lead_id == lead_id).order_by(EmailEvent.occurred_at))
        .scalars()
        .all()
    )