"""Tests for the input and output guardrails."""

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

from healthcare_assistant_lib.agent.guardrails import guardrails_node
from healthcare_assistant_lib.agent.output_guardrail import (
    SAFE_FALLBACK,
    output_guardrail_node,
    validate_answer,
)
from healthcare_assistant_lib.agent.utils import message_text


def _state(text):
    """Test helper: state."""
    return {"messages": [HumanMessage(content=text)]}


class TestInputGuardrail:
    """Tests for input guardrail."""

    def test_normal_message_passes(self):
        """Test normal message passes."""
        result = guardrails_node(_state("what is ibuprofen?"))
        assert result["blocked"] is False
        assert result["emergency"] is False

    def test_empty_message_blocked(self):
        """Test empty message blocked."""
        result = guardrails_node(_state("   "))
        assert result["blocked"] is True

    def test_emergency_detected(self):
        """Test emergency detected."""
        result = guardrails_node(_state("I think I'm having a heart attack"))
        assert result["blocked"] is True
        assert result["emergency"] is True
        assert "emergency" in message_text(result["messages"][0]).lower()

    def test_off_topic_blocked(self):
        """Test off topic blocked."""
        result = guardrails_node(_state("write code for a website"))
        assert result["blocked"] is True
        assert result["emergency"] is False

    def test_resets_per_turn_fields(self):
        """Test resets per turn fields."""
        result = guardrails_node(_state("hello"))
        assert result["handled"] is False
        assert result["specialty"] == ""


class TestOutputGuardrail:
    """Tests for output guardrail."""

    def test_safe_answer_detected(self):
        """Test safe answer detected."""
        assert validate_answer("Ibuprofen is a common pain reliever. See a doctor.") == []

    def test_general_you_have_is_not_flagged(self):
        """Test general you have is not flagged."""
        assert validate_answer("For your legs, you have several good options.") == []

    def test_definitive_diagnosis_flagged(self):
        """Test definitive diagnosis flagged."""
        assert validate_answer("Based on this, you probably have the flu.")
        assert validate_answer("It sounds like you have the flu.")

    def test_dosing_flagged(self):
        """Test dosing flagged."""
        assert validate_answer("Take 2 tablets now.")
        assert validate_answer("Use 500 mg twice a day.")

    def test_stop_medication_flagged(self):
        """Test stop medication flagged."""
        assert validate_answer("You should stop taking your blood pressure pills.")

    def test_node_passes_safe_answer(self):
        """Test node passes safe answer."""
        state = {"messages": [AIMessage(content="Here is some general info.", id="a1")]}
        assert output_guardrail_node(state) == {}

    def test_node_replaces_unsafe_answer(self):
        """Test node replaces unsafe answer."""
        state = {"messages": [AIMessage(content="You have diabetes. Take 500 mg daily.", id="a1")]}
        result = output_guardrail_node(state)
        kinds = [type(m) for m in result["messages"]]
        assert RemoveMessage in kinds
        assert any(message_text(m) == SAFE_FALLBACK for m in result["messages"])
