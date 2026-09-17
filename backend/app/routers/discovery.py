from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_api_token
from app.db.database import get_db
from app.db.models import Campaign
from app.schemas.discovery import DiscoveryResult
from app.services.discovery import run_discovery

router = APIRouter(prefix="/campaigns", tags=["discovery"], dependencies=[Depends(require_api_token)])


@router.post("/{campaign_id}/discover", response_model=DiscoveryResult, status_code=status.HTTP_201_CREATED)
def discover(campaign_id: int, db: Session = Depends(get_db)) -> DiscoveryResult:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")

    result = run_discovery(db, campaign)
    return DiscoveryResult(
        created_count=len(result["created"]),
        rejected_count=len(result["rejected"]),
        created_lead_ids=[lead.id for lead in result["created"]],
        rejected=[{"reason": r["reason"]} for r in result["rejected"]],
    )