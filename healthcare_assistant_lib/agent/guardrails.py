"""Input guardrail node — first node on every turn.

Two jobs:

1. Screen the incoming message: block empty or clearly off-topic requests, and
   detect possible emergencies (red-flag phrases) so we can point the user to
   real help instead of chatting.
2. Reset the per-turn control fields so a turn never inherits stale routing/answer
   state from the previous one.

The checks are rule-based keyword matches — deterministic, free and fast. A
production system might use an LLM classifier here.
"""

from langchain_core.messages import AIMessage

from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.utils import message_text
from healthcare_assistant_lib.constants import EMERGENCY_MESSAGE

_EMERGENCY = (
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "can not breathe",
    "difficulty breathing",
    "trouble breathing",
    "shortness of breath",
    "heart attack",
    "stroke",
    "severe bleeding",
    "bleeding a lot",
    "unconscious",
    "unresponsive",
    "seizure",
    "overdose",
    "anaphylaxis",
    "suicidal",
    "kill myself",
    "end my life",
    "want to die",
)

_OFF_TOPIC = (
    "write code",
    "stock price",
    "bitcoin",
    "hack ",
    "write me a poem",
    "translate this",
)

_RESET = {
    "handled": False,
    "blocked": False,
    "emergency": False,
    "fell_back": False,
    "specialty": "",
}


def guardrails_node(state: AssistantState) -> dict:
    """Screen the incoming message and reset per-turn state."""
    text = message_text(state["messages"][-1]).strip().lower()

    if not text:
        return {
            **_RESET,
            "blocked": True,
            "messages": [
                AIMessage(
                    content="Please share a health-related question and I'll do my best to help."
                )
            ],
        }

    if any(term in text for term in _EMERGENCY):
        return {
            **_RESET,
            "blocked": True,
            "emergency": True,
            "messages": [AIMessage(content=EMERGENCY_MESSAGE)],
        }

    if any(term in text for term in _OFF_TOPIC):
        return {
            **_RESET,
            "blocked": True,
            "messages": [
                AIMessage(
                    content=(
                        "I can only help with general health, conditions, medications, "
                        "nutrition and fitness information."
                    )
                )
            ],
        }

    return dict(_RESET)
