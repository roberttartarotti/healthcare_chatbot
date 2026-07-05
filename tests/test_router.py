"""Tests for the supervisor/orchestrator routing logic."""

from langchain_core.messages import HumanMessage

from healthcare_assistant_lib.agent.router import classify_specialty
from tests.conftest import FakeLLM


def test_classify_returns_valid_specialty(patch_agent_llm):
    """Test classify returns valid specialty."""
    patch_agent_llm(FakeLLM(route="nutrition"))
    assert (
        classify_specialty([HumanMessage(content="how many calories in nutella?")]) == "nutrition"
    )


def test_classify_falls_back_to_general_on_unknown(patch_agent_llm):
    """Test classify falls back to general on unknown."""
    patch_agent_llm(FakeLLM(route="not-a-real-specialty"))
    assert classify_specialty([HumanMessage(content="???")]) == "general"


def test_classify_falls_back_when_llm_errors(monkeypatch):
    """Test classify falls back when llm errors."""

    class BoomLLM:
        """Test double: BoomLLM."""

        def with_structured_output(self, schema):
            """Test helper: with structured output."""
            raise RuntimeError("llm down")

    monkeypatch.setattr("healthcare_assistant_lib.agent.router.get_llm", lambda: BoomLLM())
    assert classify_specialty([HumanMessage(content="anything")]) == "general"
