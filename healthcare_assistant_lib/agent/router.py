"""Supervisor / orchestrator node.

The orchestrator is entered twice per turn (this realises the required
orchestration → agent → orchestration → user flow):

1. Before the agent: ``handled`` is False, so it CLASSIFIES the request into one
   specialty and routes there.
2. After the agent has answered: ``handled`` is True, so it does nothing and the
   graph moves on to the output guardrail and back to the user.

Routing uses the LLM as a classifier (structured output) over the specialist
descriptions, with a safe fallback to the default specialist.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from healthcare_assistant_lib.agent.llm import get_llm
from healthcare_assistant_lib.agent.specialist_agents import (
    DEFAULT_SPECIALTY,
    SPECIALISTS,
    get_specialist,
)
from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.utils import message_text

_VALID = {s.name for s in SPECIALISTS}
_OPTIONS = "\n".join(f"- {s.name}: {s.description}" for s in SPECIALISTS)
_ROUTER_PROMPT = (
    "You are the router for a healthcare assistant. Read the user's latest message "
    "and choose the single best specialist to answer it. Options:\n"
    f"{_OPTIONS}\n\n"
    "Reply with only the specialty name. If unsure, choose "
    f"'{DEFAULT_SPECIALTY}'."
)


class RouteDecision(BaseModel):
    """Structured routing output — the specialty name to route to."""

    specialty: str = Field(description="One of the specialist names listed in the prompt.")


def classify_specialty(messages: list, summary: str = "") -> str:
    """Classify the latest message into a specialty name (with safe fallback)."""
    latest = message_text(messages[-1]) if messages else ""
    system = _ROUTER_PROMPT
    if summary:
        system += f"\n\nConversation summary so far:\n{summary}"
    prompt = [SystemMessage(content=system), HumanMessage(content=latest or "(empty message)")]
    try:
        decision = get_llm().with_structured_output(RouteDecision).invoke(prompt)
        name = (decision.specialty or "").strip().lower()
    except Exception:
        name = DEFAULT_SPECIALTY
    return name if name in _VALID else DEFAULT_SPECIALTY


def supervisor_node(state: AssistantState) -> dict:
    """Route to a specialist (pre-answer) or pass through (post-answer)."""
    if state.get("handled"):
        return {}
    specialty = classify_specialty(state["messages"], state.get("summary", ""))
    return {"specialty": specialty}


def route_from_supervisor(state: AssistantState) -> str:
    """Edge: hand off to the chosen specialist, or return to the user once answered."""
    if state.get("handled"):
        return "output_guardrail"
    return get_specialist(state.get("specialty", DEFAULT_SPECIALTY)).node
