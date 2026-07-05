"""Knowledge-base specialist — the LAST-resort fallback agent.

It is not chosen by the router. It is reached only when a health specialist could
not answer (see agent/fallback.py). It searches the local vector store and answers
strictly from what it finds — otherwise it says it doesn't know.
"""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.knowledge_base import search_knowledge_base

SPECIALIST = Specialist(
    name="knowledge_base",
    node="knowledge_base_agent",
    description=(
        "Last-resort fallback: the user's own uploaded documents (local knowledge "
        "base). Reached only when no other specialist could answer."
    ),
    prompt=(
        "You are the knowledge-base specialist and the LAST resort, used only when "
        "the other specialists could not answer. Call search_knowledge_base once "
        "with the user's question. Answer ONLY using the returned chunks, and cite "
        "the source file name(s). If the tool returns not_found (nothing relevant "
        "enough), or returns nothing useful, clearly tell the user you don't know "
        "and that the answer isn't in the uploaded documents. Never use outside "
        "knowledge and never guess."
    ),
    tools=(search_knowledge_base,),
)
