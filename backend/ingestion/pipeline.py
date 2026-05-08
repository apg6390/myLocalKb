from __future__ import annotations

from pathlib import Path

from backend.config import Settings, get_settings
from backend.ingestion.chunker import chunk_text
from backend.ingestion.parsers import parse_docx, parse_pdf, parse_pptx, parse_text
from backend.retrieval.embedder import embed
from backend.retrieval.store import ChromaStore, get_store


PARSERS = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".pptx": parse_pptx,
    ".txt": parse_text,
    ".md": parse_text,
}


async def ingest_document(
    file_path: Path,
    doc_id: str,
    filename: str,
    settings: Settings | None = None,
    store: ChromaStore | None = None,
) -> int:
    resolved = settings or get_settings()
    suffix = file_path.suffix.lower()
    parser = PARSERS.get(suffix)
    if parser is None:
        raise ValueError(f"Unsupported file type: {suffix}")

    pages = parser(file_path)
    chunks = chunk_text(
        pages,
        chunk_size=resolved.retrieval.chunk_size,
        overlap=resolved.retrieval.chunk_overlap,
    )
    embeddings = await embed([chunk["text"] for chunk in chunks], resolved.embeddings)
    (store or get_store()).add_chunks(doc_id, filename, chunks, embeddings)
    return len(chunks)
