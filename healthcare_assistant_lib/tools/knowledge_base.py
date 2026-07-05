"""Knowledge-base tool — search the local vector store of uploaded documents.

Used only by the fallback knowledge-base agent. Returns chunks whose similarity
is at/above the configured threshold (see rag/store.py); if none qualify, returns
not_found so the agent can say it doesn't know.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.rag import store
from healthcare_assistant_lib.tools._client import not_found, unavailable


class KnowledgeBaseInput(BaseModel):
    """Pydantic input schema for the knowledge-base tool."""

    query: str = Field(description="What to look up in the uploaded documents.")


@tool(args_schema=KnowledgeBaseInput)
def search_knowledge_base(query: str) -> dict:
    """Search the user's uploaded documents (local vector database).

    Returns the most relevant chunks (with their source file and similarity) when
    they clear the similarity threshold, a not_found result when nothing is
    relevant enough, or an 'unavailable' result if the vector store can't be read.
    """
    try:
        chunks = store.search(query)
    except Exception:
        return unavailable("knowledge base")

    if not chunks:
        return not_found("Nothing relevant enough was found in the uploaded documents.")

    return {
        "status": "ok",
        "query": query,
        "chunks": chunks,
        "source": "local knowledge base",
    }
