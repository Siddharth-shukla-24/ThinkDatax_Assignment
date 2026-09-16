from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.db.models import EmailEventType


class EventCreate(BaseModel):
    event_type: str
    event_metadata: Optional[dict] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        valid = {e.value for e in EmailEventType}
        if v not in valid:
            raise ValueError(f"event_type must be one of {sorted(valid)}")
        return v


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    event_type: str
    occurred_at: datetime
    event_metadata: Optional[dict]