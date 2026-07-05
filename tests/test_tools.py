"""Tests for the six open-API tools.

Each tool is checked on three paths, using canned bodies shaped like the real
APIs (captured from live calls):

- ok        — a valid upstream body parses into the expected result,
- not_found — upstream 404 / empty result returns status "not_found",
- unavailable — an upstream failure returns status "unavailable".
"""

from healthcare_assistant_lib.tools.conditions import search_medical_conditions
from healthcare_assistant_lib.tools.drug_label import lookup_drug_label
from healthcare_assistant_lib.tools.drug_names import search_drug_names
from healthcare_assistant_lib.tools.exercises import search_exercises
from healthcare_assistant_lib.tools.health_topics import search_health_topics
from healthcare_assistant_lib.tools.nutrition import lookup_food_nutrition

UNAVAILABLE_MESSAGE = "temporarily not available"


_OPENFDA = {
    "results": [
        {
            "openfda": {
                "brand_name": ["Advil"],
                "generic_name": ["IBUPROFEN"],
                "manufacturer_name": ["Pfizer"],
            },
            "purpose": ["Pain reliever"],
            "indications_and_usage": ["For temporary relief of minor aches and pains"],
            "warnings": ["Allergy alert: ibuprofen may cause a severe allergic reaction"],
            "adverse_reactions": ["Stomach upset"],
        }
    ]
}


class TestDrugLabel:
    """Tests for drug label."""

    def test_ok(self, patch_json):
        """Test ok."""
        patch_json(_OPENFDA)
        result = lookup_drug_label.invoke({"name": "advil"})
        assert result["status"] == "ok"
        assert result["name"] == "Advil"
        assert "Pain reliever" in result["purpose"]
        assert result["source"] == "openFDA"

    def test_not_found_on_404(self, patch_json):
        """Test not found on 404."""
        patch_json(None)
        result = lookup_drug_label.invoke({"name": "zzznotadrug"})
        assert result["status"] == "not_found"

    def test_not_found_on_empty_results(self, patch_json):
        """Test not found on empty results."""
        patch_json({"results": []})
        result = lookup_drug_label.invoke({"name": "zzznotadrug"})
        assert result["status"] == "not_found"

    def test_unavailable(self, patch_json):
        """Test unavailable."""
        patch_json(raises=True)
        result = lookup_drug_label.invoke({"name": "advil"})
        assert result["status"] == "unavailable"
        assert UNAVAILABLE_MESSAGE in result["message"]


_RXNORM = {
    "drugGroup": {
        "conceptGroup": [
            {
                "tty": "IN",
                "conceptProperties": [{"rxcui": "5640", "name": "ibuprofen", "tty": "IN"}],
            },
            {
                "tty": "BN",
                "conceptProperties": [{"rxcui": "153010", "name": "Advil", "tty": "BN"}],
            },
        ]
    }
}


class TestDrugNames:
    """Tests for drug names."""

    def test_ok(self, patch_json):
        """Test ok."""
        patch_json(_RXNORM)
        result = search_drug_names.invoke({"name": "ibuprofen"})
        assert result["status"] == "ok"
        assert result["count"] == 2
        rxcuis = {c["rxcui"] for c in result["concepts"]}
        assert {"5640", "153010"} <= rxcuis

    def test_not_found_when_no_concepts(self, patch_json):
        """Test not found when no concepts."""
        patch_json({"drugGroup": {"conceptGroup": [{"tty": "BN"}]}})
        result = search_drug_names.invoke({"name": "zzz"})
        assert result["status"] == "not_found"

    def test_not_found_on_none(self, patch_json):
        """Test not found on none."""
        patch_json(None)
        result = search_drug_names.invoke({"name": "zzz"})
        assert result["status"] == "not_found"

    def test_unavailable(self, patch_json):
        """Test unavailable."""
        patch_json(raises=True)
        result = search_drug_names.invoke({"name": "ibuprofen"})
        assert result["status"] == "unavailable"


_MEDLINE_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<nlmSearchResult><list>"
    '<document rank="0" url="https://medlineplus.gov/headache.html">'
    '<content name="title">&lt;span class="qt0"&gt;Headache&lt;/span&gt;</content>'
    '<content name="FullSummary">A headache is pain in the head.</content>'
    "</document>"
    "</list></nlmSearchResult>"
)


class TestHealthTopics:
    """Tests for health topics."""

    def test_ok(self, patch_text):
        """Test ok."""
        patch_text(_MEDLINE_XML)
        result = search_health_topics.invoke({"query": "headache"})
        assert result["status"] == "ok"
        topic = result["topics"][0]
        assert topic["title"] == "Headache"
        assert topic["url"] == "https://medlineplus.gov/headache.html"
        assert "pain in the head" in topic["summary"]

    def test_not_found_on_none(self, patch_text):
        """Test not found on none."""
        patch_text(None)
        result = search_health_topics.invoke({"query": "zzz"})
        assert result["status"] == "not_found"

    def test_not_found_on_empty_list(self, patch_text):
        """Test not found on empty list."""
        patch_text("<nlmSearchResult><list></list></nlmSearchResult>")
        result = search_health_topics.invoke({"query": "zzz"})
        assert result["status"] == "not_found"

    def test_unavailable_on_malformed_xml(self, patch_text):
        """Test unavailable on malformed xml."""
        patch_text("this is not xml <<<")
        result = search_health_topics.invoke({"query": "headache"})
        assert result["status"] == "unavailable"

    def test_unavailable(self, patch_text):
        """Test unavailable."""
        patch_text(raises=True)
        result = search_health_topics.invoke({"query": "headache"})
        assert result["status"] == "unavailable"


_CONDITIONS = [2, ["366", "30572"], None, [["Asthma", "J45.909"], ["Asthma - mild", "J45.30"]]]


class TestMedicalConditions:
    """Tests for medical conditions."""

    def test_ok(self, patch_json):
        """Test ok."""
        patch_json(_CONDITIONS)
        result = search_medical_conditions.invoke({"query": "asthma"})
        assert result["status"] == "ok"
        assert result["total"] == 2
        assert result["conditions"][0] == {"name": "Asthma", "icd10cm": "J45.909"}

    def test_not_found_on_zero(self, patch_json):
        """Test not found on zero."""
        patch_json([0, [], None, []])
        result = search_medical_conditions.invoke({"query": "zzz"})
        assert result["status"] == "not_found"

    def test_not_found_on_none(self, patch_json):
        """Test not found on none."""
        patch_json(None)
        result = search_medical_conditions.invoke({"query": "zzz"})
        assert result["status"] == "not_found"

    def test_unavailable(self, patch_json):
        """Test unavailable."""
        patch_json(raises=True)
        result = search_medical_conditions.invoke({"query": "asthma"})
        assert result["status"] == "unavailable"


_PRODUCT = {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "nutriscore_grade": "e",
    "nova_group": 4,
    "nutriments": {"energy-kcal_100g": 539, "sugars_100g": 56.3, "fat_100g": 30.9},
}
_OFF_SEARCH = {"count": 1, "products": [_PRODUCT]}
_OFF_BARCODE = {"code": "3017624010701", "product": _PRODUCT}


class TestNutrition:
    """Tests for nutrition."""

    def test_ok_by_name(self, patch_json):
        """Test ok by name."""
        patch_json(_OFF_SEARCH)
        result = lookup_food_nutrition.invoke({"query": "nutella"})
        assert result["status"] == "ok"
        assert result["product_name"] == "Nutella"
        assert result["nutriscore_grade"] == "E"
        assert result["nova_group"] == 4
        assert result["nutriments_per_100g"]["energy_kcal"] == 539

    def test_ok_by_barcode(self, patch_json):
        """Test ok by barcode."""
        patch_json(_OFF_BARCODE)
        result = lookup_food_nutrition.invoke({"query": "3017624010701"})
        assert result["status"] == "ok"
        assert result["product_name"] == "Nutella"

    def test_not_found_on_empty_search(self, patch_json):
        """Test not found on empty search."""
        patch_json({"count": 0, "products": []})
        result = lookup_food_nutrition.invoke({"query": "zzznotafood"})
        assert result["status"] == "not_found"

    def test_unavailable(self, patch_json):
        """Test unavailable."""
        patch_json(raises=True)
        result = lookup_food_nutrition.invoke({"query": "nutella"})
        assert result["status"] == "unavailable"


_EXERCISES = [
    {
        "name": "Barbell Bench Press",
        "level": "intermediate",
        "equipment": "barbell",
        "primaryMuscles": ["chest"],
        "category": "strength",
        "instructions": ["Lie on the bench.", "Press the bar up.", "Lower it slowly."],
    },
    {
        "name": "Squat",
        "level": "beginner",
        "equipment": "barbell",
        "primaryMuscles": ["quadriceps"],
        "category": "strength",
        "instructions": ["Stand tall.", "Squat down."],
    },
]


class TestExercises:
    """Tests for exercises."""

    def test_ok(self, patch_json):
        """Test ok."""
        patch_json(_EXERCISES)
        result = search_exercises.invoke({"query": "bench"})
        assert result["status"] == "ok"
        assert result["count"] == 1
        exercise = result["exercises"][0]
        assert exercise["name"] == "Barbell Bench Press"
        assert exercise["primary_muscles"] == ["chest"]
        assert len(exercise["instructions"]) == 2

    def test_not_found(self, patch_json):
        """Test not found."""
        patch_json(_EXERCISES)
        result = search_exercises.invoke({"query": "swimming"})
        assert result["status"] == "not_found"

    def test_unavailable_on_none(self, patch_json):
        """Test unavailable on none."""
        patch_json(None)
        result = search_exercises.invoke({"query": "bench"})
        assert result["status"] == "unavailable"

    def test_unavailable(self, patch_json):
        """Test unavailable."""
        patch_json(raises=True)
        result = search_exercises.invoke({"query": "bench"})
        assert result["status"] == "unavailable"
