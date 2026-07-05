"""Summarization node — keep the context window bounded on long conversations.

Answer to "can we summarise old messages after ~30 messages?": yes. Once the
history grows past a threshold, we ask the LLM to fold the older messages into a
running summary (stored on the state) and then DELETE those older messages with
RemoveMessage. Specialists receive the summary in their system prompt, so nothing
is lost — the model keeps the gist while the token cost stays flat.

Important detail: we only ever cut at a HumanMessage boundary (a turn boundary),
so we never orphan a tool_result from its tool_call — which would otherwise make
the provider reject the next request.
"""

from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage

from healthcare_assistant_lib.agent.llm import get_llm
from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.utils import message_text

SUMMARY_THRESHOLD = 30
KEEP_RECENT_TURNS = 3

_SUMMARY_INSTRUCTION = (
    "You maintain a running summary of a healthcare-assistant conversation. "
    "Produce a concise, updated summary that captures the user's questions, the "
    "topics and specialists involved, any stable context about the user, and key "
    "information already given. Keep it factual and short."
)


def _cutoff_index(messages: list) -> int:
    """Index of the first message to KEEP (older ones are summarised & removed).

    Returns 0 (meaning "don't summarise") unless there are enough complete turns
    to safely trim while keeping the most recent ones.
    """
    human_indexes = [i for i, m in enumerate(messages) if isinstance(m, HumanMessage)]
    if len(human_indexes) <= KEEP_RECENT_TURNS:
        return 0
    return human_indexes[-KEEP_RECENT_TURNS]


def summarize_node(state: AssistantState) -> dict:
    """Fold older messages into the running summary and delete them."""
    messages = state["messages"]
    if len(messages) < SUMMARY_THRESHOLD:
        return {}

    cutoff = _cutoff_index(messages)
    if cutoff <= 0:
        return {}

    older = messages[:cutoff]
    previous = state.get("summary", "")

    prompt = [SystemMessage(content=_SUMMARY_INSTRUCTION)]
    if previous:
        prompt.append(SystemMessage(content=f"Existing summary:\n{previous}"))
    prompt.extend(older)
    prompt.append(HumanMessage(content="Give the updated summary now."))

    summary = message_text(get_llm().invoke(prompt))
    removals = [RemoveMessage(id=m.id) for m in older]
    return {"summary": summary, "messages": removals}
