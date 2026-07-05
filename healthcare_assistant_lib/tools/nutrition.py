"""Nutrition tool — Open Food Facts, no API key required.

Looks up a packaged food product by barcode (all-digit input) or by name search,
and returns its Nutri-Score, NOVA processing group and key per-100g nutrients.

API: https://world.openfoodfacts.org  (ODbL open data, no key; send a User-Agent)
Note: Open Food Facts is packaged/branded-product oriented — great for a specific
product, weaker for generic whole foods.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{code}.json"
_SEARCH_URL = "https://world.openfoodfacts.org/api/v2/search"
_FIELDS = "product_name,brands,nutriscore_grade,nova_group,nutriments"
_SERVICE = "Open Food Facts"


class NutritionInput(BaseModel):
    """Pydantic input schema for the nutrition tool."""

    query: str = Field(description="A food product name, or a product barcode (digits only)")


def _summarise(product: dict, query: str) -> dict:
    """Shape a raw Open Food Facts product into a compact nutrition summary."""
    nutriments = product.get("nutriments", {}) or {}
    return {
        "status": "ok",
        "query": query,
        "product_name": product.get("product_name") or "",
        "brands": product.get("brands") or "",
        "nutriscore_grade": (product.get("nutriscore_grade") or "").upper(),
        "nova_group": product.get("nova_group"),
        "nutriments_per_100g": {
            "energy_kcal": nutriments.get("energy-kcal_100g"),
            "carbohydrates_g": nutriments.get("carbohydrates_100g"),
            "sugars_g": nutriments.get("sugars_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "saturated_fat_g": nutriments.get("saturated-fat_100g"),
            "proteins_g": nutriments.get("proteins_100g"),
            "salt_g": nutriments.get("salt_100g"),
            "fiber_g": nutriments.get("fiber_100g"),
        },
        "source": "Open Food Facts",
    }


@tool(args_schema=NutritionInput)
def lookup_food_nutrition(query: str) -> dict:
    """Look up a packaged food's nutrition (Nutri-Score, NOVA group, per-100g
    nutrients) by barcode or name. Returns a not_found result if no product
    matches, or an 'unavailable' result if the service cannot be reached.
    """
    text = query.strip()
    try:
        if text.isdigit():
            data = _client.get_json(_BARCODE_URL.format(code=text), params={"fields": _FIELDS})
            product = (data or {}).get("product") if isinstance(data, dict) else None
        else:
            data = _client.get_json(
                _SEARCH_URL,
                params={"search_terms": text, "fields": _FIELDS, "page_size": 1},
            )
            products = (data or {}).get("products") if isinstance(data, dict) else None
            product = products[0] if products else None
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    if not product:
        return not_found(f"No food product found for '{query}'.")

    return _summarise(product, query)
