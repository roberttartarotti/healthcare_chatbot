"""General specialist — the default, backed by MedlinePlus health topics."""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.health_topics import search_health_topics

SPECIALIST = Specialist(
    name="general",
    node="general_agent",
    description=(
        "General health questions, greetings, or anything that does not clearly "
        "fit the other specialists."
    ),
    prompt=(
        "You are the general health specialist and the default. Use "
        "search_health_topics for reliable consumer-health information. If a "
        "question really belongs to another area, still answer helpfully at a "
        "general level."
    ),
    tools=(search_health_topics,),
)
