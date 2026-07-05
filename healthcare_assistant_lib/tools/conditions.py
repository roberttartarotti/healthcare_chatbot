"""Conditions tool — NIH Clinical Table Search Service, no API key required.

Searches the NLM's list of medical conditions and returns matches with their
ICD-10-CM codes. Good for mapping a symptom/condition phrase to recognised
condition names and codes.

API: https://clinicaltables.nlm.nih.gov/api/conditions/v3/search  (no key)
The endpoint returns a compact JSON array::

    [ total, [codes], extraData, [[name, icd10cm_codes], ...] ]
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_URL = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
_SERVICE = "NIH Clinical Tables"
_MAX_LIST = 5


class ConditionsInput(BaseModel):
    """Pydantic input schema for the conditions tool."""

    query: str = Field(description="Condition or symptom to look up, e.g. 'asthma'")


@tool(args_schema=ConditionsInput)
def search_medical_conditions(query: str) -> dict:
    """Search a medical-conditions reference and return matches with ICD-10-CM codes.

    Returns a not_found result if nothing matches, or an 'unavailable' result if
    the service cannot be reached.
    """
    try:
        data = _client.get_json(
            _URL,
            params={
                "terms": query.strip(),
                "maxList": _MAX_LIST,
                "df": "primary_name,icd10cm_codes",
            },
        )
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    if not isinstance(data, list) or len(data) < 4:
        return not_found(f"No conditions found for '{query}'.")

    total, rows = data[0], data[3]
    if not total or not rows:
        return not_found(f"No conditions found for '{query}'.")

    conditions = [
        {"name": row[0], "icd10cm": row[1] if len(row) > 1 else ""} for row in rows if row
    ]
    return {
        "status": "ok",
        "query": query,
        "total": total,
        "conditions": conditions,
        "source": "NIH Clinical Tables",
    }
