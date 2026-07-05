"""Tool registry.

One tool per open, no-registration public API:

- lookup_drug_label       — openFDA drug labels
- search_drug_names       — RxNorm / RxNav drug-name normalisation
- search_health_topics    — MedlinePlus consumer-health topics
- search_medical_conditions — NIH Clinical Tables (conditions + ICD-10-CM)
- lookup_food_nutrition   — Open Food Facts nutrition
- search_exercises        — free-exercise-db exercises

Every tool degrades gracefully: on any upstream failure it returns a
``{"status": "unavailable", ...}`` result instead of raising (see ``_client``).
"""

from healthcare_assistant_lib.tools.conditions import search_medical_conditions
from healthcare_assistant_lib.tools.drug_label import lookup_drug_label
from healthcare_assistant_lib.tools.drug_names import search_drug_names
from healthcare_assistant_lib.tools.exercises import search_exercises
from healthcare_assistant_lib.tools.health_topics import search_health_topics
from healthcare_assistant_lib.tools.nutrition import lookup_food_nutrition

ALL_TOOLS = [
    lookup_drug_label,
    search_drug_names,
    search_health_topics,
    search_medical_conditions,
    lookup_food_nutrition,
    search_exercises,
]
