"""Conditions & symptoms specialist — MedlinePlus + NIH Clinical Tables."""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.conditions import search_medical_conditions
from healthcare_assistant_lib.tools.health_topics import search_health_topics

SPECIALIST = Specialist(
    name="conditions",
    node="conditions_agent",
    description=(
        "Questions about symptoms, illnesses, conditions, or general 'what is X / "
        "what should I know about X' health topics."
    ),
    prompt=(
        "You are the conditions & symptoms specialist. Use search_health_topics "
        "for patient-friendly explanations from MedlinePlus and "
        "search_medical_conditions to find recognised condition names and "
        "ICD-10 codes. Explain in general terms; never tell the user what they have."
    ),
    tools=(search_medical_conditions, search_health_topics),
)
