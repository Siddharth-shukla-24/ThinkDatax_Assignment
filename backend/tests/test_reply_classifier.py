import uuid

import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import engine, get_db
from app.db.models import Campaign, Company, Lead, LeadStatus
from app.main import app
from app.services.reply_classifier import _fallback_classify, classify_reply

client = TestClient(app)
HEADERS = {"Authorization": f"Bearer {settings.api_token}"}


@pytest.fixture(autouse=True)
def db_session():
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield session
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def lead_id(db_session):
    unique = uuid.uuid4().hex[:8]
    company = Company(name=f"Test Co Reply {unique}")
    campaign = Campaign(name=f"Test Campaign Reply {unique}", icp_criteria={})
    db_session.add_all([company, campaign])
    db_session.flush()
    lead = Lead(
        company_id=company.id,
        campaign_id=campaign.id,
        first_name="Jamie",
        email=f"jamie.replytest.{unique}@example.com",
        source_url="https://example.com",
        status=LeadStatus.SENT.value,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead.id


@pytest.mark.parametrize(
    "text,expected_label",
    [
        ("Sounds great, let's schedule a call this week!", "Interested"),
        ("Not interested, we already have a vendor for this.", "Not Interested"),
        ("Please unsubscribe me from this list.", "Unsubscribe Request"),
        ("Bad timing, maybe circle back next quarter.", "Needs Follow-up"),
        ("Who is this? I don't recognize this email.", "Other"),
    ],
)
def test_fallback_classifier_labels(text, expected_label):
    result = _fallback_classify(text)
    assert result["label"] == expected_label


def test_classify_reply_fills_draft_response_when_missing():
    result = classify_reply("Jamie", "Not interested, thanks.")
    assert result["draft_response"]
    assert "{first_name}" not in result["draft_response"]


def test_classify_reply_requires_auth(lead_id):
    r = client.post(f"/leads/{lead_id}/classify-reply", json={"reply_text": "Interested!"})
    assert r.status_code == 401


def test_classify_reply_404_for_unknown_lead():
    r = client.post("/leads/999999/classify-reply", json={"reply_text": "Interested!"}, headers=HEADERS)
    assert r.status_code == 404


def test_classify_reply_full_round_trip(lead_id):
    r = client.post(
        f"/leads/{lead_id}/classify-reply",
        json={"reply_text": "This looks interesting, can we set up a call?"},
        headers=HEADERS,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["label"] in {"Interested", "Not Interested", "Needs Follow-up", "Unsubscribe Request", "Other"}
    assert body["draft_response"]
    assert 0.0 <= body["confidence"] <= 1.0

    events = client.get(f"/leads/{lead_id}/events", headers=HEADERS).json()
    assert any(
        e["event_type"] == "replied" and e["event_metadata"].get("classification") for e in events
    )