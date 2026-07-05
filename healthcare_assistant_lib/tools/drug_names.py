"""Drug-name tool — RxNorm / RxNav (NIH/NLM), no API key required.

Resolves a typed drug name to standardised RxNorm concepts: ingredients, brand
names and clinical drugs, each with its RxCUI code. Useful for confirming what a
medicine is and finding its brand/generic equivalents.

API: https://rxnav.nlm.nih.gov/REST/drugs.json  (~20 req/s, no key, no auth)
Note: the RxNav drug-drug *interaction* API was discontinued in Jan 2024; this
tool uses the still-supported drug-concept endpoint only.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_URL = "https://rxnav.nlm.nih.gov/REST/drugs.json"
_SERVICE = "RxNorm (RxNav)"
_MAX_CONCEPTS = 12


class DrugNamesInput(BaseModel):
    """Pydantic input schema for the drug-name tool."""

    name: str = Field(description="A drug name to standardise, e.g. 'advil' or 'ibuprofen'")


@tool(args_schema=DrugNamesInput)
def search_drug_names(name: str) -> dict:
    """Standardise a drug name into RxNorm concepts (ingredients, brands, clinical
    drugs) with their RxCUI codes. Returns a not_found result if the name matches
    nothing, or an 'unavailable' result if the service cannot be reached.
    """
    try:
        data = _client.get_json(_URL, params={"name": name.strip()})
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    groups = ((data or {}).get("drugGroup") or {}).get("conceptGroup") or []
    concepts = []
    for group in groups:
        tty = group.get("tty")
        for prop in group.get("conceptProperties") or []:
            concepts.append(
                {
                    "rxcui": prop.get("rxcui"),
                    "name": prop.get("name"),
                    "tty": prop.get("tty", tty),
                }
            )

    if not concepts:
        return not_found(f"No RxNorm concepts found for '{name}'.")

    return {
        "status": "ok",
        "query": name,
        "count": len(concepts),
        "concepts": concepts[:_MAX_CONCEPTS],
        "source": "RxNorm (RxNav)",
    }
