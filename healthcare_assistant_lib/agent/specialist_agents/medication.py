"""Medication specialist — drug information via openFDA + RxNorm."""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.drug_label import lookup_drug_label
from healthcare_assistant_lib.tools.drug_names import search_drug_names

SPECIALIST = Specialist(
    name="medication",
    node="medication_agent",
    description=(
        "Questions about a specific medicine or drug: what it is, its uses, "
        "side effects, warnings, or its brand/generic names."
    ),
    prompt=(
        "You are the medication specialist. Use lookup_drug_label for a drug's "
        "official FDA information (purpose, uses, warnings, side effects) and "
        "search_drug_names to resolve or disambiguate a drug's brand/generic "
        "names. Summarise what the label says; do not add dosing advice."
    ),
    tools=(lookup_drug_label, search_drug_names),
)
