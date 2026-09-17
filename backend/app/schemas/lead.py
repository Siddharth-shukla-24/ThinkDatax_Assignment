from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.campaign import CampaignRead
from app.schemas.company import CompanyRead
from app.schemas.score import ScoreRead


class LeadCreate(BaseModel):
    company_id: int
    campaign_id: int
    first_name: str
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: EmailStr
    source_url: str
    raw_data: Optional[dict] = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    campaign_id: int
    first_name: str
    last_name: Optional[str]
    title: Optional[str]
    email: str
    source_url: str
    status: str
    created_at: datetime
    score: Optional[ScoreRead] = None


class LeadDetail(LeadRead):
    company: CompanyRead
    campaign: CampaignRead