from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    size: Optional[str] = None
    raw_data: Optional[dict] = None


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: Optional[str]
    industry: Optional[str]
    region: Optional[str]
    size: Optional[str]
    created_at: datetime
    raw_data: Optional[dict] = None