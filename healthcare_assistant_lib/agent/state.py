"""Graph state.

The state flows between nodes. ``messages`` is the conversation (the add_messages
reducer appends, and RemoveMessage entries delete). Per-turn control fields
(handled/blocked/emergency/specialty) are reset by the guardrails node at the
start of every turn; ``summary`` persists across turns (running conversation
summary produced by the summarize node).
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AssistantState(TypedDict):
    """Shared state passed between graph nodes.

    Fields::

        messages: the running conversation.
        specialty: the specialist chosen by the supervisor.
        handled: True once a specialist has produced a final answer this turn.
        blocked: set by the input guardrail; True means refuse and stop.
        emergency: set by the input guardrail; True means a possible emergency.
        fell_back: True once this turn has handed off to the knowledge-base agent.
        summary: running summary of older messages (see summarize.py).
    """

    messages: Annotated[list, add_messages]
    specialty: str
    handled: bool
    blocked: bool
    emergency: bool
    fell_back: bool
    summary: str
