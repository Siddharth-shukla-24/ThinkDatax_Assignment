import base64

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import EmailEventType, Lead
from app.services.events import record_event
from app.services.tokens import verify_unsubscribe_token

router = APIRouter(tags=["tracking"])

_PIXEL_GIF = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")


@router.get("/track/pixel/{lead_id}")
def track_pixel(lead_id: int, db: Session = Depends(get_db)) -> Response:
    lead = db.get(Lead, lead_id)
    if lead is not None:
        record_event(db, lead, EmailEventType.OPENED.value)
        db.commit()
    return Response(content=_PIXEL_GIF, media_type="image/gif")


@router.get("/unsubscribe/{token}", response_class=HTMLResponse)
def unsubscribe(token: str, db: Session = Depends(get_db)) -> str:
    lead_id = verify_unsubscribe_token(token)
    if lead_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired unsubscribe link."
        )
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    record_event(db, lead, EmailEventType.UNSUBSCRIBED.value)
    db.commit()

    return "<html><body><p>You have been unsubscribed and will not receive further emails from us.</p></body></html>"