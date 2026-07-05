"""Shared definitions for the specialist agents.

Each specialist lives in its own module and exposes a single ``SPECIALIST``
instance of the ``Specialist`` type defined here. The registry
(``specialist_agents/__init__.py``) collects them.
"""

from dataclasses import dataclass

from langchain_core.tools import BaseTool

SAFETY_PREAMBLE = (
    "You are one specialist in a homemade, educational healthcare assistant. This "
    "is NOT a medical service and has no medical value. Follow these rules strictly:\n"
    "- Give only general, educational information grounded in your tools' results.\n"
    "- NEVER diagnose the user or state that they have a condition.\n"
    "- NEVER give specific dosages, or tell anyone to start, stop, or change a medication.\n"
    "- NEVER guarantee outcomes or claim to cure anything.\n"
    "- Use your tools to get information. If a tool result has status 'unavailable', "
    "tell the user that data source is temporarily unavailable and suggest trying "
    "later. If status is 'not_found', say you couldn't find reliable information and "
    "do not invent any.\n"
    "- Always encourage consulting a qualified healthcare professional for anything personal.\n"
    "- Be clear and concise, and cite which source (e.g. openFDA, MedlinePlus) you used."
)


@dataclass(frozen=True)
class Specialist:
    """A specialist agent: how the supervisor picks it and how it behaves."""

    name: str
    node: str
    description: str
    prompt: str
    tools: tuple[BaseTool, ...]


def build_system_prompt(specialist: Specialist, summary: str = "") -> str:
    """Compose a specialist's full system prompt (safety + persona + summary)."""
    parts = [SAFETY_PREAMBLE, specialist.prompt]
    if summary:
        parts.append(f"Summary of the earlier conversation:\n{summary}")
    return "\n\n".join(parts)
