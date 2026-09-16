from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    icp_criteria: Optional[dict] = None


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    icp_criteria: Optional[dict]
    created_at: datetime