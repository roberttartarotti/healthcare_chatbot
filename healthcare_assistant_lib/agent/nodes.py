"""Specialist agent nodes.

Each specialist is the same shape — an LLM bound to that specialist's tools, told
its persona — so we build them from the registry with a factory. The node lets the
LLM converse and call tools (dynamic tool loop): while it emits tool calls the
graph routes to the shared tools node and back; when it produces a plain answer,
``handled`` flips True and control returns to the supervisor.
"""

from langchain_core.messages import SystemMessage

from healthcare_assistant_lib.agent.llm import get_llm
from healthcare_assistant_lib.agent.specialist_agents import Specialist, build_system_prompt
from healthcare_assistant_lib.agent.state import AssistantState


def make_specialist_node(specialist: Specialist):
    """Build the graph node function for a specialist."""

    def specialist_node(state: AssistantState) -> dict:
        """Run the specialist's LLM: converse, call tools, or produce the answer."""
        llm = get_llm().bind_tools(specialist.tools)
        system = build_system_prompt(specialist, state.get("summary", ""))
        response = llm.invoke([SystemMessage(content=system), *state["messages"]])
        has_tool_calls = bool(getattr(response, "tool_calls", None))
        return {"messages": [response], "handled": not has_tool_calls}

    return specialist_node


def _wants_tools(state: AssistantState) -> bool:
    """True if the last message asked to call tools."""
    return bool(getattr(state["messages"][-1], "tool_calls", None))


def route_health_specialist(state: AssistantState) -> str:
    """Edge for health specialists: run tools, else go to the fallback grader."""
    return "tools" if _wants_tools(state) else "grade"


def route_knowledge_base(state: AssistantState) -> str:
    """Edge for the KB agent: run tools, else hand straight back to the supervisor."""
    return "tools" if _wants_tools(state) else "supervisor"


def route_from_tools(state: AssistantState) -> str:
    """Edge: after running tools, return to the specialist that called them."""
    from healthcare_assistant_lib.agent.specialist_agents import get_specialist

    return get_specialist(state.get("specialty", "")).node
