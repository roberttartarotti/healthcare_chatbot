"""Health-topics tool — MedlinePlus (NIH/NLM), no API key required.

Searches MedlinePlus, the NLM's consumer-health encyclopedia, and returns
patient-friendly topic summaries with links. The service replies in XML (there is
no JSON option), so we parse it here.

API: https://wsearch.nlm.nih.gov/ws/query  (~85 req/min per IP, no key)
"""

import html
import re
from xml.etree import ElementTree

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_URL = "https://wsearch.nlm.nih.gov/ws/query"
_SERVICE = "MedlinePlus"
_MAX_TOPICS = 3
_MAX_SUMMARY = 500
_TAG_RE = re.compile(r"<[^>]+>")


class HealthTopicsInput(BaseModel):
    """Pydantic input schema for the health-topics tool."""

    query: str = Field(description="Health topic or symptom to look up, e.g. 'headache'")


def _clean(text: str | None) -> str:
    """Strip the highlight markup / HTML MedlinePlus embeds and unescape entities."""
    if not text:
        return ""
    return html.unescape(_TAG_RE.sub("", text)).strip()


@tool(args_schema=HealthTopicsInput)
def search_health_topics(query: str) -> dict:
    """Search MedlinePlus for consumer-health information on a topic or symptom.

    Returns up to a few topic summaries with links. Returns a not_found result if
    nothing matches, or an 'unavailable' result if the service cannot be reached.
    """
    try:
        text = _client.get_text(
            _URL, params={"db": "healthTopics", "term": query.strip(), "retmax": _MAX_TOPICS}
        )
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    if not text:
        return not_found(f"No MedlinePlus topics found for '{query}'.")

    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return unavailable(_SERVICE)

    topics = []
    for document in root.findall(".//document"):
        fields = {c.get("name"): c.text for c in document.findall("content")}
        topics.append(
            {
                "title": _clean(fields.get("title")),
                "url": document.get("url"),
                "summary": _clean(fields.get("FullSummary"))[:_MAX_SUMMARY],
            }
        )

    if not topics:
        return not_found(f"No MedlinePlus topics found for '{query}'.")

    return {"status": "ok", "query": query, "topics": topics, "source": "MedlinePlus"}
