from pydantic import BaseModel


class ReplyClassifyRequest(BaseModel):
    reply_text: str


class ReplyClassification(BaseModel):
    label: str
    confidence: float
    reasoning: str
    draft_response: str