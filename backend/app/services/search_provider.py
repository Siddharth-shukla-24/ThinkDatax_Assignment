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
        {
        "title": "Target names Cara Sylvester Chief Merchandising Officer",
        "url": "https://corporate.target.com/about/leadership-team/cara-sylvester",
        "snippet": (
            "Target named Cara Sylvester chief merchandising officer effective February 2026. "
            "She leads assortment, product development, product design, partner collaborations, "
            "and merchandising capabilities."
        ),
    },
    {
        "title": "Under Armour names Kara Trent Chief Merchandising Officer",
        "url": "https://about.underarmour.com/en/investors/corporate-governance.html",
        "snippet": (
            "Under Armour says Kara Trent has served as chief merchandising officer since "
            "February 2026. Her background includes North America merchandising and EMEA "
            "merchandising and planning roles across product, brand and marketplace engines."
        ),
    },
    {
        "title": "lululemon leadership Elizabeth Binder Chief Merchandising Officer",
        "url": "https://corporate.lululemon.com/about-us/leadership-team",
        "snippet": (
            "lululemon identifies Elizabeth Binder as chief merchandising officer. She leads "
            "global product strategy and assortment architecture and oversees global and regional "
            "merchandising teams and merchandising and planning operations."
        ),
    },
    {
        "title": "Macy's Nata Dvir Chief Merchandising Officer",
        "url": "https://investors.macysinc.com/newsroom/news/news-details/2026/Macys-Welcomes-Retail-Veteran-Dayna-Ziegler-as-Senior-Vice-President-General-Merchandise-Manager--Ready-to-Wear--2026-uiByYhCj0k/",
        "snippet": (
            "Macy's identifies Nata Dvir as chief merchandising officer. In 2026 Macy's said "
            "its Ready-to-Wear leadership would report to Dvir while the company strengthens "
            "assortments and responds to market trends and evolving demand."
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