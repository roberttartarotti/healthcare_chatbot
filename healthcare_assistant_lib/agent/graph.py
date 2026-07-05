"""Graph assembly — a supervisor (orchestrator) multi-agent system with a
knowledge-base fallback.

Flow::

    START
      -> guardrails            (input screen: off-topic / emergency; per-turn reset)
         -> (blocked) END
         -> summarize          (compress old messages if the history is long)
            -> supervisor      (ORCHESTRATOR: classify -> route to a specialist)
      supervisor
        -> medication_agent | conditions_agent | nutrition_agent
           | fitness_agent | general_agent            (routed by specialty)
      <health specialist>
        -> (tool calls) tools -> <same specialist>    (dynamic tool loop)
        -> (answer) grade                             (did it actually answer?)
      grade
        -> (answered / no docs) supervisor
        -> (unanswered + docs exist) knowledge_base_agent   (LAST-RESORT fallback)
      knowledge_base_agent
        -> (tool calls) tools -> knowledge_base_agent
        -> (answer) supervisor
      supervisor
        -> (already answered) output_guardrail        (safety screen)
           -> END

Every turn is orchestration -> agent -> orchestration -> user. State is persisted
with MemorySaver keyed by thread_id (= user id).
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from healthcare_assistant_lib.agent.fallback import grade_node, route_after_grade
from healthcare_assistant_lib.agent.guardrails import guardrails_node
from healthcare_assistant_lib.agent.nodes import (
    make_specialist_node,
    route_from_tools,
    route_health_specialist,
    route_knowledge_base,
)
from healthcare_assistant_lib.agent.output_guardrail import output_guardrail_node
from healthcare_assistant_lib.agent.router import route_from_supervisor, supervisor_node
from healthcare_assistant_lib.agent.specialist_agents import (
    ALL_AGENTS,
    KNOWLEDGE_BASE,
    SPECIALISTS,
)
from healthcare_assistant_lib.agent.state import AssistantState
from healthcare_assistant_lib.agent.summarize import summarize_node
from healthcare_assistant_lib.tools import ALL_TOOLS
from healthcare_assistant_lib.tools.knowledge_base import search_knowledge_base

_HEALTH_NODES = {s.node for s in SPECIALISTS}
_ALL_NODES = {a.node for a in ALL_AGENTS}
_TOOLS = [*ALL_TOOLS, search_knowledge_base]


def _after_guardrails(state: AssistantState) -> str:
    """Stop if the input was blocked, otherwise continue into the pipeline."""
    return END if state.get("blocked") else "summarize"


def build_graph() -> "StateGraph":
    """Wire nodes and edges and compile with an in-memory checkpointer."""
    graph = StateGraph(AssistantState)

    graph.add_node("guardrails", guardrails_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("grade", grade_node)
    graph.add_node("tools", ToolNode(_TOOLS))
    graph.add_node("output_guardrail", output_guardrail_node)
    for agent in ALL_AGENTS:
        graph.add_node(agent.node, make_specialist_node(agent))

    graph.add_edge(START, "guardrails")
    graph.add_conditional_edges(
        "guardrails", _after_guardrails, {"summarize": "summarize", END: END}
    )
    graph.add_edge("summarize", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {**{node: node for node in _HEALTH_NODES}, "output_guardrail": "output_guardrail"},
    )

    for specialist in SPECIALISTS:
        graph.add_conditional_edges(
            specialist.node, route_health_specialist, {"tools": "tools", "grade": "grade"}
        )

    graph.add_conditional_edges(
        "grade",
        route_after_grade,
        {"knowledge_base_agent": KNOWLEDGE_BASE.node, "supervisor": "supervisor"},
    )

    graph.add_conditional_edges(
        KNOWLEDGE_BASE.node, route_knowledge_base, {"tools": "tools", "supervisor": "supervisor"}
    )

    graph.add_conditional_edges("tools", route_from_tools, {node: node for node in _ALL_NODES})

    graph.add_edge("output_guardrail", END)

    return graph.compile(checkpointer=MemorySaver())


graph = build_graph()
