import json
import logging
from typing import Callable, Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger("app.discovery")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5"

TOOLS = [
    {
        "name": "search_web",
        "description": (
            "Search the public web for companies/people matching a query. "
            "Returns a list of results with title, url, and snippet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "fetch_url",
        "description": "Fetch the visible text content of a specific URL for closer inspection.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are a B2B sales research assistant for StyleSense AI, an apparel/fashion "
    "demand-forecasting SaaS. Given an Ideal Customer Profile (ICP), use the search_web "
    "and fetch_url tools to find 5 to 10 REAL people at REAL companies matching the ICP. "
    "For each lead you find, only include facts you can point to in the tool results you "
    "were given - never invent a name, title, company detail, or signal you did not "
    "actually see. When you are done researching, reply with ONLY a JSON array (no prose, "
    "no markdown fences) where each item has exactly these fields: first_name, last_name, "
    "title, company_name, company_domain, company_industry, company_region, company_size, "
    "source_url, observed_signal_sentence, observed_signal_short, pain_point_category, "
    "value_prop_for_pain_point, specific_context_detail, one_line_relevance_hypothesis. "
    "Use an empty string for any field you cannot ground in what you actually found - "
    "never guess."
)

_MOCK_EXTRACTIONS = {
    "https://www.meridianthreads.com/news/dtc-expansion-2026": {
        "first_name": "Taylor",
        "last_name": "Nguyen",
        "title": "Head of Merchandising",
        "company_name": "Meridian Threads",
        "company_domain": "meridianthreads.com",
        "company_industry": "Fashion",
        "company_region": "US",
        "company_size": "200-500",
        "observed_signal_sentence": "Meridian Threads announced a direct-to-consumer expansion this quarter",
        "observed_signal_short": "DTC expansion",
        "pain_point_category": "markdown-heavy end-of-season sales",
        "value_prop_for_pain_point": "cut markdown-heavy sales with AI demand forecasting",
        "specific_context_detail": "growing channel mix",
        "one_line_relevance_hypothesis": (
            "your merchandising team may be balancing inventory across more channels than before"
        ),
    },
    "https://www.northfieldapparel.com/press/leadership-update": {
        "first_name": "Priya",
        "last_name": "Shah",
        "title": "Head of Merchandising",
        "company_name": "Northfield Apparel Group",
        "company_domain": "northfieldapparel.com",
        "company_industry": "Fashion",
        "company_region": "US",
        "company_size": "500-1000",
        "observed_signal_sentence": (
            "Northfield Apparel Group named a new Head of Merchandising following a string "
            "of cross-channel stockouts"
        ),
        "observed_signal_short": "new Head of Merchandising amid stockouts",
        "pain_point_category": "cross-channel stockouts",
        "value_prop_for_pain_point": "reduce stockouts with inventory allocation optimisation",
        "specific_context_detail": "holiday season stockouts across stores and online",
        "one_line_relevance_hypothesis": (
            "inventory allocation across channels may be a growing priority for your team"
        ),
    },
        "https://corporate.target.com/about/leadership-team/cara-sylvester": {
        "first_name": "Cara",
        "last_name": "Sylvester",
        "title": "Executive Vice President and Chief Merchandising Officer",
        "company_name": "Target",
        "company_domain": "target.com",
        "company_industry": "Retail",
        "company_region": "US",
        "company_size": "",
        "observed_signal_sentence": (
            "Target named Cara Sylvester chief merchandising officer effective February 2026"
        ),
        "observed_signal_short": "new Chief Merchandising Officer",
        "pain_point_category": "assortment design",
        "value_prop_for_pain_point": "support assortment design",
        "specific_context_detail": "assortment and product development",
        "one_line_relevance_hypothesis": (
            "your merchandising team may be balancing assortment and product development"
        ),
    },
    "https://about.underarmour.com/en/investors/corporate-governance.html": {
        "first_name": "Kara",
        "last_name": "Trent",
        "title": "Chief Merchandising Officer",
        "company_name": "Under Armour",
        "company_domain": "underarmour.com",
        "company_industry": "Apparel",
        "company_region": "US",
        "company_size": "",
        "observed_signal_sentence": (
            "Under Armour says Kara Trent has served as chief merchandising officer since February 2026"
        ),
        "observed_signal_short": "new Chief Merchandising Officer",
        "pain_point_category": "merchandising and planning",
        "value_prop_for_pain_point": "support merchandising and planning",
        "specific_context_detail": "product, brand and marketplace engines",
        "one_line_relevance_hypothesis": (
            "your team may be coordinating product and merchandising planning across markets"
        ),
    },
    "https://corporate.lululemon.com/about-us/leadership-team": {
        "first_name": "Elizabeth",
        "last_name": "Binder",
        "title": "Chief Merchandising Officer",
        "company_name": "lululemon",
        "company_domain": "lululemon.com",
        "company_industry": "Apparel",
        "company_region": "US",
        "company_size": "",
        "observed_signal_sentence": (
            "lululemon identifies Elizabeth Binder as chief merchandising officer"
        ),
        "observed_signal_short": "Chief Merchandising Officer",
        "pain_point_category": "assortment architecture",
        "value_prop_for_pain_point": "support assortment architecture and planning",
        "specific_context_detail": "global and regional merchandising teams",
        "one_line_relevance_hypothesis": (
            "your team may be coordinating assortment planning across regions"
        ),
    },
    "https://investors.macysinc.com/newsroom/news/news-details/2026/Macys-Welcomes-Retail-Veteran-Dayna-Ziegler-as-Senior-Vice-President-General-Merchandise-Manager--Ready-to-Wear--2026-uiByYhCj0k/": {
        "first_name": "Nata",
        "last_name": "Dvir",
        "title": "Chief Merchandising Officer",
        "company_name": "Macy's",
        "company_domain": "macys.com",
        "company_industry": "Retail",
        "company_region": "US",
        "company_size": "",
        "observed_signal_sentence": (
            "Macy's identifies Nata Dvir as chief merchandising officer"
        ),
        "observed_signal_short": "Chief Merchandising Officer",
        "pain_point_category": "assortment planning",
        "value_prop_for_pain_point": "support assortment planning around evolving demand",
        "specific_context_detail": "Ready-to-Wear assortments and market trends",
        "one_line_relevance_hypothesis": (
            "your merchandising team may be balancing assortment breadth with changing demand"
        ),
    },
}


def _call_anthropic(messages: list) -> dict:
    response = httpx.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "tools": TOOLS,
            "messages": messages,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()


def _live_discover(
    icp: dict, run_search: Callable[[str], List[Dict]], run_fetch: Callable[[str], Dict], max_turns: int = 6
) -> List[dict]:
    messages = [
        {"role": "user", "content": f"ICP: {json.dumps(icp)}\nFind 5-10 real leads matching this ICP."}
    ]

    for _ in range(max_turns):
        result = _call_anthropic(messages)
        content = result.get("content", [])
        tool_uses = [b for b in content if b.get("type") == "tool_use"]

        if not tool_uses:
            raw_text = "\n".join(b["text"] for b in content if b.get("type") == "text").strip()
            try:
                leads = json.loads(raw_text)
            except json.JSONDecodeError:
                logger.warning("LLM did not return valid JSON leads: %s", raw_text[:300])
                return []
            return leads if isinstance(leads, list) else []

        messages.append({"role": "assistant", "content": content})
        tool_results = []
        for tool_use in tool_uses:
            name = tool_use["name"]
            tool_input = tool_use.get("input", {})
            if name == "search_web":
                output = run_search(tool_input.get("query", ""))
            elif name == "fetch_url":
                output = run_fetch(tool_input.get("url", ""))
            else:
                output = {"error": f"unknown tool {name}"}
            tool_results.append(
                {"type": "tool_result", "tool_use_id": tool_use["id"], "content": json.dumps(output)}
            )
        messages.append({"role": "user", "content": tool_results})

    logger.warning("Discovery loop hit max_turns without a final answer.")
    return []


def _build_mock_query(icp: dict) -> str:
    parts = []
    if icp.get("titles"):
        parts.append(icp["titles"][0])
    if icp.get("industry"):
        parts.append(icp["industry"])
    if icp.get("region"):
        parts.append(icp["region"])
    return " ".join(parts) or "apparel merchandising leads"


def _mock_discover(icp: dict, run_search: Callable[[str], List[Dict]]) -> List[dict]:
    results = run_search(_build_mock_query(icp))
    leads = []
    for r in results:
        extraction = _MOCK_EXTRACTIONS.get(r["url"])
        if extraction:
            leads.append({**extraction, "source_url": r["url"]})
    return leads


def discover_leads(
    icp: dict, run_search: Callable[[str], List[Dict]], run_fetch: Callable[[str], Dict]
) -> List[dict]:
    if not settings.anthropic_api_key:
        return _mock_discover(icp, run_search)
    return _live_discover(icp, run_search, run_fetch)   