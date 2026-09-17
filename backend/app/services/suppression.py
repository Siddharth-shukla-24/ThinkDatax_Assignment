from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Suppression


def _normalize(email: str) -> str:
    return email.strip().lower()


def suppress_email(db: Session, email: str, reason: str) -> None:
    normalized = _normalize(email)
    existing = db.execute(select(Suppression).where(Suppression.email == normalized)).scalar_one_or_none()
    if existing is None:
        db.add(Suppression(email=normalized, reason=reason))


def is_suppressed(db: Session, email: str) -> bool:
    normalized = _normalize(email)
    return (
        db.execute(select(Suppression).where(Suppression.email == normalized)).scalar_one_or_none()
        is not None
    )