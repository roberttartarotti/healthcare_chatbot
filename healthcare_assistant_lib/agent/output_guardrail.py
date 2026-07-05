"""Output guardrail node — screen the specialist's answer before it reaches the user.

Rule-based safety screen (deterministic, no extra LLM call). It looks for the
things this hobby project must never emit: a definitive diagnosis, specific
dosing, an instruction to start/stop medication, or a promise to cure. If any are
found, the answer is replaced with a safe fallback rather than shown.
"""

import re

from langchain_core.messages import AIMessage, RemoveMessage

from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.utils import message_text

SAFE_FALLBACK = (
    "I can't safely provide that. I can share general, educational information, but "
    "anything involving a diagnosis, specific dosages, or changing a treatment "
    "should come from a qualified healthcare professional who knows your situation."
)

_UNSAFE_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    (
        "definitive diagnosis",
        re.compile(
            r"\byou (?:have been diagnosed|are suffering from|(?:most )?likely have|"
            r"probably have|definitely have|certainly have)\b",
            re.I,
        ),
    ),
    (
        "definitive diagnosis",
        re.compile(r"\b(?:your diagnosis is|i can diagnose|it sounds like you have)\b", re.I),
    ),
    (
        "dosing instruction",
        re.compile(r"\btake\s+\d+\s*(?:mg|mcg|ml|g|tablets?|pills?|capsules?|drops?)\b", re.I),
    ),
    (
        "dosing instruction",
        re.compile(
            r"\b\d+\s?(?:mg|mcg|ml|g)\b[^.]{0,30}\b(?:every|per|a day|daily|twice|once|hourly|times a day)\b",
            re.I,
        ),
    ),
    ("stop medication", re.compile(r"\bstop (?:taking|your)\b", re.I)),
    (
        "cure guarantee",
        re.compile(r"\b(?:guaranteed to (?:cure|heal)|will cure|this will cure)\b", re.I),
    ),
)


def validate_answer(text: str) -> list[str]:
    """Return the labels of any unsafe patterns found in the answer (empty = safe)."""
    return [label for label, pattern in _UNSAFE_PATTERNS if pattern.search(text or "")]


def output_guardrail_node(state: AssistantState) -> dict:
    """Replace the answer with a safe fallback if it trips the safety screen."""
    last = state["messages"][-1]
    if not validate_answer(message_text(last)):
        return {}
    return {"messages": [RemoveMessage(id=last.id), AIMessage(content=SAFE_FALLBACK)]}
