"""Local vector store (ChromaDB) for the knowledge-base agent.

ChromaDB is embedded and persists to a folder on disk — no server, no Docker.

Embeddings (configurable via ``EMBEDDING_PROVIDER``):
- ``auto`` (default): OpenAI (``OPENAI_API_KEY``) if set, otherwise a local model.
- ``openai``: OpenAI ``text-embedding-3-small`` (needs OPENAI_API_KEY).
- ``local``: Chroma's built-in ONNX all-MiniLM-L6-v2 (no key, ~80MB one-time).

Retrieval uses COSINE distance, converted to a similarity in 0..1. Only chunks at
or above ``KB_SIMILARITY_THRESHOLD`` (default 0.9) are returned — below that we
treat the knowledge base as not having the answer.

``chromadb`` is imported lazily, so importing the rest of the app (and running its
tests) doesn't require it; if it's missing or errors, callers treat the KB as
unavailable.
"""

import contextlib
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = Path(os.getenv("KB_DOCUMENTS_DIR", _ROOT / "knowledge_base" / "documents"))
INDEX_DIR = Path(os.getenv("KB_INDEX_DIR", _ROOT / "knowledge_base" / "index"))
COLLECTION = "healthcare_docs"
_DEFAULT_THRESHOLD = 0.9


def similarity_threshold() -> float:
    """Minimum cosine similarity (0..1) for a chunk to count as an answer."""
    try:
        return float(os.getenv("KB_SIMILARITY_THRESHOLD", str(_DEFAULT_THRESHOLD)))
    except ValueError:
        return _DEFAULT_THRESHOLD


def _embedding_function():
    """Pick the embedding function from the environment (see module docstring)."""
    provider = os.getenv("EMBEDDING_PROVIDER", "auto").lower()
    use_openai = provider == "openai" or (provider == "auto" and os.getenv("OPENAI_API_KEY"))
    if use_openai:
        from chromadb.utils import embedding_functions

        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        )
    return None


def _collection():
    """Return the persistent Chroma collection (created if needed), cosine space."""
    import chromadb

    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    kwargs = {"metadata": {"hnsw:space": "cosine"}}
    embedding_function = _embedding_function()
    if embedding_function is not None:
        kwargs["embedding_function"] = embedding_function
    return client.get_or_create_collection(COLLECTION, **kwargs)


def count() -> int:
    """Number of chunks in the index (0 if the index doesn't exist / on error)."""
    if not INDEX_DIR.exists():
        return 0
    try:
        return _collection().count()
    except Exception:
        return 0


def search(query: str, k: int = 4, threshold: float | None = None) -> list[dict]:
    """Return chunks scoring at/above the similarity threshold.

    Each chunk is {text, source, similarity}. Pass ``threshold`` to override the
    env default (e.g. 0.0 to see everything with its raw score).
    """
    if not INDEX_DIR.exists():
        return []
    threshold = similarity_threshold() if threshold is None else threshold
    collection = _collection()
    if collection.count() == 0:
        return []

    result = collection.query(query_texts=[query], n_results=k)
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    chunks = []
    for text, meta, distance in zip(documents, metadatas, distances, strict=False):
        similarity = 1.0 - float(distance)
        if similarity >= threshold:
            chunks.append(
                {
                    "text": text,
                    "source": (meta or {}).get("source", ""),
                    "similarity": round(similarity, 4),
                }
            )
    return chunks


def add(chunks: list[str], metadatas: list[dict], ids: list[str]) -> None:
    """Embed and store chunks (used by the ingest command)."""
    _collection().add(documents=chunks, metadatas=metadatas, ids=ids)


def reset() -> None:
    """Drop the collection so ingestion can rebuild it from scratch."""
    import chromadb

    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    with contextlib.suppress(Exception):
        client.delete_collection(COLLECTION)
