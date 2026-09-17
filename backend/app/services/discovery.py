import logging
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Campaign, Company, Lead, LeadStatus
from app.services.llm_extractor import discover_leads
from app.services.scoring import recompute_score
from app.services.search_provider import fetch_url, search_web

logger = logging.getLogger("app.discovery")

REQUIRED_LEAD_FIELDS = ["first_name", "title", "company_name", "source_url"]
COMPANY_CLAIM_FIELDS = ["pain_point_category", "value_prop_for_pain_point", "specific_context_detail"]
LEAD_CLAIM_FIELDS = ["observed_signal_sentence", "observed_signal_short", "one_line_relevance_hypothesis"]
MAX_LEADS_PER_RUN = 10


def _is_substantiated(claim: str, source_text: str, min_overlap: float = 0.4) -> bool:
    if not claim or not source_text:
        return False
    claim_words = {w.lower().strip(".,!?;:") for w in claim.split() if len(w) > 3}
    if not claim_words:
        return False
    source_lower = source_text.lower()
    matched = sum(1 for w in claim_words if w in source_lower)
    return (matched / len(claim_words)) >= min_overlap


def _guess_email(first_name: str, last_name: str, domain: str) -> Tuple[str, str]:
    if not domain:
        return "", "no_domain"
    local = first_name.lower()
    if last_name:
        local += f".{last_name.lower()}"
    local = "".join(ch for ch in local if ch.isalnum() or ch == ".")
    return f"{local}@{domain}", "guessed_pattern"


def run_discovery(db: Session, campaign: Campaign) -> Dict:
    icp = campaign.icp_criteria or {}
    url_to_content: Dict[str, str] = {}
    seen_urls: set = set()

    def _search(query: str) -> List[Dict]:
        results = search_web(query)
        for r in results:
            url_to_content[r["url"]] = r.get("snippet", "")
            seen_urls.add(r["url"])
        return results

    def _fetch(url: str) -> Dict:
        result = fetch_url(url)
        url_to_content[url] = result.get("content", "")
        seen_urls.add(url)
        return result

    raw_leads = discover_leads(icp, run_search=_search, run_fetch=_fetch)

    created: List[Lead] = []
    rejected: List[Dict] = []

    for raw in raw_leads[:MAX_LEADS_PER_RUN]:
        missing = [f for f in REQUIRED_LEAD_FIELDS if not raw.get(f)]
        if missing:
            rejected.append({"reason": f"missing required fields: {missing}"})
            continue

        source_url = raw["source_url"]
        if source_url not in seen_urls:
            logger.info("Grounding check dropped lead: unverifiable source_url=%s", source_url)
            rejected.append({"reason": f"source_url not found in tool results: {source_url}"})
            continue

        source_text = url_to_content.get(source_url, "")
        dropped_claims = []
        company_raw_data: Dict[str, str] = {}
        lead_raw_data: Dict[str, str] = {}

        for field in COMPANY_CLAIM_FIELDS:
            value = raw.get(field, "")
            if not value:
                continue
            if _is_substantiated(value, source_text):
                company_raw_data[field] = value
            else:
                dropped_claims.append(field)

        for field in LEAD_CLAIM_FIELDS:
            value = raw.get(field, "")
            if not value:
                continue
            if _is_substantiated(value, source_text):
                lead_raw_data[field] = value
            else:
                dropped_claims.append(field)

        if dropped_claims:
            logger.info(
                "Grounding check dropped unsubstantiated claims for source_url=%s: %s",
                source_url,
                dropped_claims,
            )

        domain = (raw.get("company_domain") or "").strip().lower() or None
        company = None
        if domain:
            company = db.execute(select(Company).where(Company.domain == domain)).scalar_one_or_none()
        if company is None:
            company = db.execute(
                select(Company).where(Company.name == raw["company_name"])
            ).scalar_one_or_none()
        if company is None:
            company = Company(
                name=raw["company_name"],
                domain=domain,
                industry=raw.get("company_industry") or None,
                region=raw.get("company_region") or None,
                size=raw.get("company_size") or None,
                raw_data=company_raw_data or None,
            )
            db.add(company)
            db.flush()
        elif company_raw_data:
            company.raw_data = {**(company.raw_data or {}), **company_raw_data}

        email, email_source = _guess_email(raw["first_name"], raw.get("last_name", ""), domain or "")
        if not email:
            rejected.append({"reason": "could not derive an email (no company domain found)"})
            continue

        existing_lead = db.execute(select(Lead).where(Lead.email == email)).scalar_one_or_none()
        if existing_lead is not None:
            rejected.append({"reason": f"lead with email {email} already exists"})
            continue

        lead_raw_data["email_source"] = email_source
        lead_raw_data["discovery_mode"] = "live" if settings.anthropic_api_key else "mock"

        lead = Lead(
            company_id=company.id,
            campaign_id=campaign.id,
            first_name=raw["first_name"],
            last_name=raw.get("last_name") or None,
            title=raw.get("title") or None,
            email=email,
            source_url=source_url,
            status=LeadStatus.NEW.value,
            raw_data=lead_raw_data,
        )
        db.add(lead)
        db.flush()

        recompute_score(db, lead)
        created.append(lead)

    db.commit()
    for lead in created:
        db.refresh(lead)

    return {"created": created, "rejected": rejected}