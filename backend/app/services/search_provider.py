import logging
from typing import Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger("app.discovery")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"

_MOCK_RESULTS = [
    {
        "title": "Meridian Threads launches DTC expansion and opens Head of Merchandising role",
        "url": "https://www.meridianthreads.com/news/dtc-expansion-2026",
        "snippet": (
            "Meridian Threads, a mid-size apparel retailer, announced a direct-to-consumer "
            "expansion this quarter and is hiring a Head of Merchandising to manage inventory "
            "across its growing channel mix. The company cited markdown-heavy end-of-season "
            "sales as a key challenge it is working to address."
        ),
    },
    {
        "title": "Northfield Apparel Group promotes new Head of Merchandising amid stockouts",
        "url": "https://www.northfieldapparel.com/press/leadership-update",
        "snippet": (
            "Northfield Apparel Group named a new Head of Merchandising following a string of "
            "cross-channel stockouts during its holiday season, as the fashion brand looks to "
            "improve inventory allocation across stores and its online marketplace."
        ),
    },
]


def search_web(query: str) -> List[Dict]:
    if not settings.tavily_api_key:
        logger.info("MOCK SEARCH (no TAVILY_API_KEY configured) query=%r", query)
        return list(_MOCK_RESULTS)

    response = httpx.post(
        TAVILY_SEARCH_URL,
        json={"api_key": settings.tavily_api_key, "query": query, "max_results": 8},
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
        for r in data.get("results", [])
    ]


def fetch_url(url: str) -> Dict:
    if not settings.tavily_api_key:
        logger.info("MOCK FETCH (no TAVILY_API_KEY configured) url=%r", url)
        for r in _MOCK_RESULTS:
            if r["url"] == url:
                return {"url": url, "content": r["snippet"]}
        return {"url": url, "content": ""}

    try:
        response = httpx.get(url, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        return {"url": url, "content": response.text[:5000]}
    except httpx.HTTPError as exc:
        logger.warning("fetch_url failed for %s: %s", url, exc)
        return {"url": url, "content": "", "error": str(exc)}