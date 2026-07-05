"""Public entry point for the assistant.

One function, ``send_message(user_id, message)``. The ``user_id`` is the LangGraph
thread_id, so each user gets an isolated, persistent conversation (MemorySaver).

The mandatory disclaimer is enforced here: it is prepended to the very first reply
of every conversation, so it is always the first thing the user sees.
"""

from langchain_core.messages import HumanMessage

from healthcare_assistant_lib.agent.graph import graph
from healthcare_assistant_lib.agent.utils import message_text
from healthcare_assistant_lib.constants import DISCLAIMER


def _config(user_id: str) -> dict:
    """Build the LangGraph config that ties a run to a user's thread."""
    return {"configurable": {"thread_id": user_id}}


def _is_new_conversation(config: dict) -> bool:
    """True if this thread has no prior messages (so the disclaimer is due)."""
    try:
        snapshot = graph.get_state(config)
    except Exception:
        return True
    return not (snapshot.values or {}).get("messages")


def send_message(user_id: str, message: str) -> dict:
    """Send a user message and return the assistant's reply.

    Returns ``{"reply", "specialty", "blocked"}``. On the first message of a
    conversation the reply is prefixed with the mandatory disclaimer.
    """
    config = _config(user_id)
    first_turn = _is_new_conversation(config)

    result = graph.invoke({"messages": [HumanMessage(content=message)]}, config)

    reply = message_text(result["messages"][-1])
    if first_turn:
        reply = f"{DISCLAIMER}\n\n{reply}"

    return {
        "reply": reply,
        "specialty": result.get("specialty", ""),
        "blocked": bool(result.get("blocked", False)),
    }
