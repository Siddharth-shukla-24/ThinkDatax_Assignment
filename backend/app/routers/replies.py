from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import EmailEventType, Lead
from app.schemas.reply import ReplyClassification, ReplyClassifyRequest
from app.services.events import record_event
from app.services.reply_classifier import classify_reply

router = APIRouter(prefix="/leads", tags=["replies"], dependencies=[Depends(require_api_token)])


@router.post(
    "/{lead_id}/classify-reply", response_model=ReplyClassification, status_code=status.HTTP_200_OK
)
def classify_lead_reply(
    lead_id: int, payload: ReplyClassifyRequest, db: Session = Depends(get_db)
) -> ReplyClassification:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    result = classify_reply(lead.first_name, payload.reply_text)

    record_event(
        db,
        lead,
        EmailEventType.REPLIED.value,
        event_metadata={"reply_text": payload.reply_text, "classification": result},
    )
    db.commit()

    return ReplyClassification(**result)