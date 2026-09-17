from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import EmailEvent, Lead
from app.schemas.event import EventCreate, EventRead
from app.services.events import record_event

router = APIRouter(
    prefix="/leads/{lead_id}/events", tags=["events"], dependencies=[Depends(require_api_token)]
)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(lead_id: int, payload: EventCreate, db: Session = Depends(get_db)) -> EmailEvent:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    event = record_event(db, lead, payload.event_type, payload.event_metadata)

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