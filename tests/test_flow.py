"""End-to-end flow tests for the multi-agent graph (stubbed LLM, offline).

Exercises the full pipeline via the public ``send_message``: routing, the tool
loop, both guardrails, the mandatory disclaimer, and per-user memory isolation.
"""

from langchain_core.messages import AIMessage

from healthcare_assistant_lib import send_message
from healthcare_assistant_lib.agent.output_guardrail import SAFE_FALLBACK
from healthcare_assistant_lib.constants import DISCLAIMER

_DISCLAIMER_MARK = "PLEASE READ FIRST"


def _ai(text):
    """Test helper: ai."""
    return AIMessage(content=text)


def _tool_call(name, args):
    """Test helper: tool call."""
    return AIMessage(
        content="", tool_calls=[{"name": name, "args": args, "id": "c1", "type": "tool_call"}]
    )


def test_direct_answer_routes_and_prepends_disclaimer(patch_agent_llm):
    """Test direct answer routes and prepends disclaimer."""
    from tests.conftest import FakeLLM

    patch_agent_llm(FakeLLM(route="general", script=[_ai("Here is some general info.")]))
    result = send_message("flow-direct", "tell me about staying healthy")

    assert result["specialty"] == "general"
    assert "Here is some general info." in result["reply"]
    assert _DISCLAIMER_MARK in result["reply"]


def test_tool_loop_then_answer(patch_agent_llm, patch_text):
    """Test tool loop then answer."""
    from tests.conftest import FakeLLM

    patch_text(
        "<nlmSearchResult><list>"
        '<document rank="0" url="https://medlineplus.gov/headache.html">'
        '<content name="title">Headache</content>'
        '<content name="FullSummary">A headache is pain in the head.</content>'
        "</document></list></nlmSearchResult>"
    )
    patch_agent_llm(
        FakeLLM(
            route="conditions",
            script=[
                _tool_call("search_health_topics", {"query": "headache"}),
                _ai("MedlinePlus says a headache is pain in the head."),
            ],
        )
    )

    result = send_message("flow-tools", "what is a headache?")
    assert result["specialty"] == "conditions"
    assert "pain in the head" in result["reply"]


def test_emergency_short_circuits(patch_agent_llm):
    """Test emergency short circuits."""
    from tests.conftest import FakeLLM

    patch_agent_llm(FakeLLM())
    result = send_message("flow-emergency", "I have severe chest pain and can't breathe")
    assert result["blocked"] is True
    assert "emergency" in result["reply"].lower()


def test_off_topic_is_blocked(patch_agent_llm):
    """Test off topic is blocked."""
    from tests.conftest import FakeLLM

    patch_agent_llm(FakeLLM())
    result = send_message("flow-offtopic", "write code to scrape a stock price")
    assert result["blocked"] is True
    assert "general health" in result["reply"].lower()


def test_output_guardrail_sanitises_unsafe_answer(patch_agent_llm):
    """Test output guardrail sanitises unsafe answer."""
    from tests.conftest import FakeLLM

    patch_agent_llm(
        FakeLLM(route="conditions", script=[_ai("You have diabetes. Take 500 mg twice a day.")])
    )
    result = send_message("flow-unsafe", "what do my symptoms mean?")
    assert SAFE_FALLBACK in result["reply"]
    assert "you have diabetes" not in result["reply"].lower()


def test_disclaimer_only_on_first_turn_and_isolated_per_user(patch_agent_llm):
    """Test disclaimer only on first turn and isolated per user."""
    from tests.conftest import FakeLLM

    patch_agent_llm(FakeLLM(route="general"))

    first = send_message("mem-a", "hello")
    assert _DISCLAIMER_MARK in first["reply"]

    second = send_message("mem-a", "another question")
    assert _DISCLAIMER_MARK not in second["reply"]

    other_user = send_message("mem-b", "hello")
    assert _DISCLAIMER_MARK in other_user["reply"]


def test_disclaimer_constant_is_used():
    """Test disclaimer constant is used."""
    assert _DISCLAIMER_MARK in DISCLAIMER
