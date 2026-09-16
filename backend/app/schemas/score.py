from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    value: int
    fit_component: int
    engagement_component: int
    updated_at: datetime


class ScoreHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_score: Optional[int]
    new_score: int
    reason: str
    created_at: datetime