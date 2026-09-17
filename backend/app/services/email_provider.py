import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("app.email")

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to: str, subject: str, html: str, text: str) -> dict:
    if not settings.resend_api_key:
        logger.info("MOCK SEND (no RESEND_API_KEY configured) to=%s subject=%r", to, subject)
        return {"id": "mock-email-id", "mocked": True}

    response = httpx.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": settings.resend_from_email,
            "to": [to],
            "subject": subject,
            "html": html,
            "text": text,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()