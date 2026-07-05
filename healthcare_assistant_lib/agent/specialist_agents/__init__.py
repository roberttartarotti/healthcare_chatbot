"""Specialist agent registry.

``SPECIALISTS`` are the router-choosable health specialists (one module each).
``KNOWLEDGE_BASE`` is a special last-resort agent the router never picks — it's
reached only via the fallback path (see agent/fallback.py). ``ALL_AGENTS`` is
everything the graph builds a node for.

EXTENSIBLE: add a new ``<name>.py`` exposing a ``SPECIALIST`` and import it into
``SPECIALISTS`` below — the graph builds its node and the router offers it
automatically.
"""

from healthcare_assistant_lib.agent.specialist_agents.base import (
    SAFETY_PREAMBLE,
    Specialist,
    build_system_prompt,
)
from healthcare_assistant_lib.agent.specialist_agents.conditions import SPECIALIST as CONDITIONS
from healthcare_assistant_lib.agent.specialist_agents.fitness import SPECIALIST as FITNESS
from healthcare_assistant_lib.agent.specialist_agents.general import SPECIALIST as GENERAL
from healthcare_assistant_lib.agent.specialist_agents.knowledge_base import (
    SPECIALIST as KNOWLEDGE_BASE,
)
from healthcare_assistant_lib.agent.specialist_agents.medication import SPECIALIST as MEDICATION
from healthcare_assistant_lib.agent.specialist_agents.nutrition import SPECIALIST as NUTRITION

SPECIALISTS: tuple[Specialist, ...] = (MEDICATION, CONDITIONS, NUTRITION, FITNESS, GENERAL)

ALL_AGENTS: tuple[Specialist, ...] = (*SPECIALISTS, KNOWLEDGE_BASE)

DEFAULT_SPECIALTY = GENERAL.name

_BY_NAME = {s.name: s for s in ALL_AGENTS}


def get_specialist(name: str) -> Specialist:
    """Look up any agent (incl. the fallback) by name, defaulting to general."""
    return _BY_NAME.get(name, _BY_NAME[DEFAULT_SPECIALTY])


__all__ = [
    "SPECIALISTS",
    "ALL_AGENTS",
    "KNOWLEDGE_BASE",
    "DEFAULT_SPECIALTY",
    "Specialist",
    "SAFETY_PREAMBLE",
    "build_system_prompt",
    "get_specialist",
]
