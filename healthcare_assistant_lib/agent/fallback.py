"""Fallback grading — decide whether to hand off to the knowledge-base agent.

Option A: after a health specialist answers, if the answer looks like a
non-answer ("I couldn't find…", "I don't know…") AND the local knowledge base
actually has documents, we remove that non-answer and route to the knowledge-base
agent for one attempt. It then answers from the vector store or says it doesn't
know. This runs at most once per turn (guarded by ``fell_back``).
"""

from langchain_core.messages import RemoveMessage

from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.utils import message_text
from healthcare_assistant_lib.rag import store

_UNANSWERED = (
    "i don't know",
    "i do not know",
    "i don't have",
    "i do not have",
    "don't have any information",
    "do not have any information",
    "couldn't find",
    "could not find",
    "couldn’t find",
    "can't find",
    "cannot find",
    "can not find",
    "not able to find",
    "unable to find",
    "can't verify",
    "cannot verify",
    "couldn't verify",
    "can't confirm",
    "cannot confirm",
    "couldn't confirm",
    "no reliable information",
    "no information",
    "no record",
    "not aware of",
    "not familiar with",
    "isn't something i can help",
    "not able to help",
    "temporarily unavailable",
    "can't help with that",
    "cannot help with that",
)


def _looks_unanswered(text: str) -> bool:
    """True if the answer reads like the specialist couldn't help."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in _UNANSWERED)


def grade_node(state: AssistantState) -> dict:
    """If the specialist didn't answer and docs exist, set up the KB fallback."""
    if state.get("fell_back"):
        return {}

    try:
        has_documents = store.count() > 0
    except Exception:
        has_documents = False
    if not has_documents:
        return {}

    last = state["messages"][-1]
    if not _looks_unanswered(message_text(last)):
        return {}

    return {
        "fell_back": True,
        "specialty": "knowledge_base",
        "messages": [RemoveMessage(id=last.id)],
    }


def route_after_grade(state: AssistantState) -> str:
    """Edge: go to the knowledge-base agent if we decided to fall back."""
    return "knowledge_base_agent" if state.get("fell_back") else "supervisor"
