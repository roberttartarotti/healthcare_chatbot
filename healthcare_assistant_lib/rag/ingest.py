"""Ingest documents into the local vector store.

Reads every supported file in ``knowledge_base/documents/`` (.txt, .md, .pdf),
splits it into overlapping chunks, embeds them with Chroma's local model, and
stores them. Run it whenever you add or change documents:

    python -m healthcare_assistant_lib.rag.ingest      # or: healthcare-assistant-ingest
"""

from pathlib import Path

from healthcare_assistant_lib.rag import store

SUPPORTED = {".txt", ".md", ".pdf"}
_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 150


def _read(path: Path) -> str:
    """Extract plain text from a supported file (empty string if unreadable)."""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return ""


def _chunk(text: str, size: int = _CHUNK_SIZE, overlap: int = _CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks, preferring to break on whitespace."""
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    start, length = 0, len(text)
    while start < length:
        end = min(start + size, length)
        if end < length:
            boundary = text.rfind("\n", start, end)
            if boundary <= start:
                boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest() -> int:
    """(Re)build the index from the documents folder. Returns the chunk count."""
    documents_dir = store.DOCUMENTS_DIR
    files = sorted(
        p for p in documents_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED
    )
    if not files:
        print(f"No documents found in {documents_dir} (supported: {', '.join(sorted(SUPPORTED))}).")
        return 0

    store.reset()
    total = 0
    for path in files:
        source = str(path.relative_to(documents_dir))
        chunks = _chunk(_read(path))
        if not chunks:
            print(f"  {source}: skipped (no extractable text)")
            continue
        store.add(
            chunks=chunks,
            metadatas=[{"source": source} for _ in chunks],
            ids=[f"{source}::{i}" for i in range(len(chunks))],
        )
        total += len(chunks)
        print(f"  {source}: {len(chunks)} chunks")

    print(f"\nIngested {total} chunks from {len(files)} file(s) into {store.INDEX_DIR}")
    return total


def main() -> None:
    """Console-script entry point."""
    ingest()


if __name__ == "__main__":
    main()
