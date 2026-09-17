import hashlib
import hmac
from typing import Optional

from app.core.config import settings


def _sign(payload: str) -> str:
    return hmac.new(settings.app_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]


def make_unsubscribe_token(lead_id: int) -> str:
    payload = str(lead_id)
    return f"{payload}.{_sign(payload)}"


def verify_unsubscribe_token(token: str) -> Optional[int]:
    try:
        payload, signature = token.split(".", 1)
        lead_id = int(payload)
    except (ValueError, AttributeError):
        return None
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    return lead_id