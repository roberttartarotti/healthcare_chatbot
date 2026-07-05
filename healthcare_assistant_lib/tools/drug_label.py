"""Drug-label tool — openFDA (US FDA), no API key required.

Looks up the official FDA drug label for a medicine by brand or generic name and
returns the human-readable sections (purpose, uses, warnings, side effects).

API: https://api.fda.gov/drug/label.json  (240 req/min, 1000/day per IP, no key)
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_URL = "https://api.fda.gov/drug/label.json"
_SERVICE = "openFDA drug label"
_MAX_CHARS = 800


class DrugLabelInput(BaseModel):
    """Pydantic input schema — the LLM reads these descriptions to fill the args."""

    name: str = Field(description="Medicine brand or generic name, e.g. 'ibuprofen' or 'Advil'")


def _clip(section: object) -> str:
    """Join a label section (list of long strings) into one clipped string."""
    if isinstance(section, list):
        text = " ".join(str(part) for part in section)
    else:
        text = str(section or "")
    text = text.strip()
    return text[:_MAX_CHARS] + "…" if len(text) > _MAX_CHARS else text


@tool(args_schema=DrugLabelInput)
def lookup_drug_label(name: str) -> dict:
    """Look up the official FDA drug label for a medicine (by brand or generic name).

    Returns general reference information: purpose, indications, warnings and
    adverse reactions. Returns a not_found result if the medicine is not in the
    FDA labels, or an 'unavailable' result if the service cannot be reached.
    """
    query = name.strip()
    search = f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"'
    try:
        data = _client.get_json(_URL, params={"search": search, "limit": 1})
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    results = (data or {}).get("results") if isinstance(data, dict) else None
    if not results:
        return not_found(f"No FDA drug label found for '{name}'.")

    label = results[0]
    openfda = label.get("openfda", {})
    display_name = (openfda.get("brand_name") or openfda.get("generic_name") or [query])[0]
    return {
        "status": "ok",
        "name": display_name,
        "generic_name": openfda.get("generic_name", []),
        "brand_name": openfda.get("brand_name", []),
        "manufacturer": openfda.get("manufacturer_name", []),
        "purpose": _clip(label.get("purpose")),
        "indications_and_usage": _clip(label.get("indications_and_usage")),
        "warnings": _clip(label.get("warnings")),
        "adverse_reactions": _clip(label.get("adverse_reactions")),
        "source": "openFDA",
    }
