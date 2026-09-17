import json
import logging
from typing import Dict

import httpx

from app.core.config import settings

logger = logging.getLogger("app.replies")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5"

LABELS = ["Interested", "Not Interested", "Needs Follow-up", "Unsubscribe Request", "Other"]

SYSTEM_PROMPT = (
    "You classify inbound sales email replies for StyleSense AI, a B2B apparel/fashion "
    "demand-forecasting SaaS. Read the reply and respond with ONLY a JSON object (no prose, "
    "no markdown fences) with exactly these fields: "
    f'"label" (one of {LABELS}), "confidence" (0.0-1.0), "reasoning" (one sentence), '
    '"draft_response" (a short, polite reply a salesperson could send, first person, signed '
    "with the sender's name if given). Base the label strictly on the reply text."
)

_KEYWORD_RULES = [
    ("Unsubscribe Request", ["unsubscribe", "remove me", "stop emailing", "opt out", "opt-out", "take me off"]),
    ("Not Interested", ["not interested", "no thanks", "not a fit", "pass on this", "not the right time", "no longer"]),
    ("Interested", ["interested", "sounds good", "sounds useful", "sounds great", "let's talk", "lets talk", "talk it through", "schedule a call", "tell me more", "sign me up", "book a", "set up a call"]),
    ("Needs Follow-up", ["follow up", "circle back", "check back", "maybe later", "reach out again", "not right now but", "next quarter"]),
]

_DRAFT_TEMPLATES = {
    "Interested": (
        "Hi {first_name},\n\nGreat to hear! I'd love to find 15 minutes to walk you through how "
        "StyleSense AI could help. Does later this week work for a quick call?\n\nBest,\n{sender_name}"
    ),
    "Not Interested": (
        "Hi {first_name},\n\nThanks for the honest reply - appreciate you taking the time to "
        "respond. I'll close this out on my end. Wishing you and the team a great season.\n\n"
        "Best,\n{sender_name}"
    ),
    "Needs Follow-up": (
        "Hi {first_name},\n\nCompletely understand the timing isn't right today. Mind if I check "
        "back in a bit? Happy to work around whatever timeline suits you.\n\nBest,\n{sender_name}"
    ),
    "Unsubscribe Request": (
        "Hi {first_name},\n\nDone - you've been removed from our list and won't hear from us "
        "again. Apologies for the inconvenience.\n\nBest,\n{sender_name}"
    ),
    "Other": (
        "Hi {first_name},\n\nThanks for getting back to me - could you tell me a bit more about "
        "what you're looking for so I can point you in the right direction?\n\nBest,\n{sender_name}"
    ),
}


def _call_anthropic(lead_first_name: str, reply_text: str) -> dict:
    response = httpx.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 500,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Lead first name: {lead_first_name}\nSender name: {settings.sender_name}\n"
                        f"Reply text:\n{reply_text}"
                    ),
                }
            ],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def _fallback_classify(reply_text: str) -> Dict:
    lowered = reply_text.lower()
    for label, keywords in _KEYWORD_RULES:
        matched = [kw for kw in keywords if kw in lowered]
        if matched:
            return {
                "label": label,
                "confidence": 0.6,
                "reasoning": f"Keyword fallback matched: {matched[0]!r}",
                "draft_response": "",
            }
    return {
        "label": "Other",
        "confidence": 0.4,
        "reasoning": "No matching keywords found; defaulted to Other.",
        "draft_response": "",
    }


def _live_classify(lead_first_name: str, reply_text: str) -> Dict:
    try:
        result = _call_anthropic(lead_first_name, reply_text)
    except httpx.HTTPError as exc:
        logger.warning("Reply classifier live call failed, falling back: %s", exc)
        return _fallback_classify(reply_text)

    raw_text = "\n".join(b["text"] for b in result.get("content", []) if b.get("type") == "text").strip()
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("Reply classifier LLM did not return valid JSON: %s", raw_text[:300])
        return _fallback_classify(reply_text)

    label = parsed.get("label")
    if label not in LABELS:
        logger.warning("Reply classifier LLM returned unknown label: %r", label)
        return _fallback_classify(reply_text)

    return {
        "label": label,
        "confidence": float(parsed.get("confidence", 0.5)),
        "reasoning": str(parsed.get("reasoning", "")),
        "draft_response": str(parsed.get("draft_response", "")),
    }


def classify_reply(lead_first_name: str, reply_text: str) -> Dict:
    if settings.anthropic_api_key:
        result = _live_classify(lead_first_name, reply_text)
    else:
        result = _fallback_classify(reply_text)

    if not result.get("draft_response"):
        template = _DRAFT_TEMPLATES.get(result["label"], _DRAFT_TEMPLATES["Other"])
        result["draft_response"] = template.format(
            first_name=lead_first_name or "there", sender_name=settings.sender_name
        )

    return result