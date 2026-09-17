from typing import List

from pydantic import BaseModel


class RejectedLead(BaseModel):
    reason: str


class DiscoveryResult(BaseModel):
    created_count: int
    rejected_count: int
    created_lead_ids: List[int]
    rejected: List[RejectedLead]