from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pagination import Page, PageParams, paginate
from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import Campaign
from app.schemas.campaign import CampaignCreate, CampaignRead

router = APIRouter(
    prefix="/campaigns", tags=["campaigns"], dependencies=[Depends(require_api_token)]
)


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> Campaign:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=Page[CampaignRead])
def list_campaigns(params: PageParams = Depends(), db: Session = Depends(get_db)) -> Page:
    stmt = select(Campaign).order_by(Campaign.created_at.desc())
    return paginate(db, stmt, params)


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign