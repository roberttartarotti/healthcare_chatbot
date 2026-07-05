"""Tests for the summarization node (context-window management)."""

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

from healthcare_assistant_lib.agent import summarize
from healthcare_assistant_lib.agent.summarize import summarize_node
from tests.conftest import FakeLLM


def _history(turns):
    """Build `turns` Human/AI turns with stable ids."""
    messages = []
    for i in range(turns):
        messages.append(HumanMessage(content=f"question {i}", id=f"h{i}"))
        messages.append(AIMessage(content=f"answer {i}", id=f"a{i}"))
    return messages


def test_below_threshold_is_noop(monkeypatch):
    """Test below threshold is noop."""
    monkeypatch.setattr(summarize, "get_llm", lambda: FakeLLM(summary_text="S"))
    state = {"messages": _history(5), "summary": ""}
    assert summarize_node(state) == {}


def test_summarises_and_removes_old_messages(monkeypatch):
    """Test summarises and removes old messages."""
    monkeypatch.setattr(summarize, "get_llm", lambda: FakeLLM(summary_text="Running summary."))
    messages = _history(16)
    result = summarize_node({"messages": messages, "summary": ""})

    assert result["summary"] == "Running summary."
    removals = result["messages"]
    assert removals and all(isinstance(m, RemoveMessage) for m in removals)

    assert len(removals) == 26
    assert isinstance(messages[len(removals)], HumanMessage)


def test_keeps_boundary_when_few_turns(monkeypatch):
    """Test keeps boundary when few turns."""
    monkeypatch.setattr(summarize, "get_llm", lambda: FakeLLM(summary_text="S"))
    messages = [HumanMessage(content="start", id="h0")]
    messages += [AIMessage(content=f"a{i}", id=f"a{i}") for i in range(30)]
    result = summarize_node({"messages": messages, "summary": ""})
    assert result == {}
