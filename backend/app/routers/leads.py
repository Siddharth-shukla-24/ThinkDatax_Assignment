from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.pagination import Page, PageParams, paginate
from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import Campaign, Company, Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadDetail, LeadRead

router = APIRouter(prefix="/leads", tags=["leads"], dependencies=[Depends(require_api_token)])


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    if db.get(Company, payload.company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    if db.get(Campaign, payload.campaign_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")

    lead = Lead(status=LeadStatus.NEW.value, **payload.model_dump())
    db.add(lead)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lead with this email already exists.",
        )
    db.refresh(lead)
    return lead


@router.get("", response_model=Page[LeadRead])
def list_leads(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    campaign_id: Optional[int] = Query(default=None),
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
) -> Page:
    stmt = select(Lead)
    if status_filter is not None:
        stmt = stmt.where(Lead.status == status_filter)
    if campaign_id is not None:
        stmt = stmt.where(Lead.campaign_id == campaign_id)
    stmt = stmt.order_by(Lead.created_at.desc())
    return paginate(db, stmt, params)


@router.get("/{lead_id}", response_model=LeadDetail)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")
    return lead