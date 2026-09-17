from types import SimpleNamespace

from app.services.scoring import _compute_fit, _compute_engagement, recompute_score


class FakeResult:
    def __init__(self, values):
        self.values = values

    def scalars(self):
        return self

    def all(self):
        return self.values


class FakeDB:
    def __init__(self, event_types=None):
        self.event_types = event_types or []
        self.added = []

    def execute(self, _statement):
        return FakeResult(self.event_types)

    def add(self, obj):
        self.added.append(obj)


def make_lead():
    company = SimpleNamespace(
        industry="Fashion",
        region="US",
        size="500-1000",
    )
    campaign = SimpleNamespace(
        icp_criteria={
            "titles": ["Head of Merchandising"],
            "industry": "Fashion",
            "region": "US",
            "company_size": "500-1000",
        }
    )
    return SimpleNamespace(
        id=1,
        title="Head of Merchandising",
        company=company,
        campaign=campaign,
        score=None,
    )


def test_compute_fit_full_match():
    points, reasons = _compute_fit(make_lead())

    assert points == 60
    assert len(reasons) == 4


def test_compute_fit_no_match():
    lead = make_lead()
    lead.title = "Intern"
    lead.company.industry = "Finance"
    lead.company.region = "India"
    lead.company.size = "1-10"

    points, reasons = _compute_fit(lead)

    assert points == 0
    assert reasons == []


def test_compute_engagement_uses_best_event():
    db = FakeDB(["sent", "opened", "replied"])

    points, unsubscribed, reasons = _compute_engagement(db, 1)

    assert points == 40
    assert unsubscribed is False
    assert "replied" in reasons[0]


def test_recompute_score_unsubscribed_cap():
    lead = make_lead()
    db = FakeDB(["sent", "opened", "replied", "unsubscribed"])

    score = recompute_score(db, lead)

    assert score.value == 5
    assert score.fit_component == 60
    assert score.engagement_component == 40
    assert len(db.added) == 2
    assert "capped: lead unsubscribed" in db.added[-1].reason