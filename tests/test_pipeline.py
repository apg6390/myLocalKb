from pathlib import Path

import pytest

from backend.config import (
    EmbeddingSettings,
    LlmSettings,
    RetrievalSettings,
    ServerSettings,
    Settings,
    StorageSettings,
)
from backend.ingestion.pipeline import ingest_document


class FakeStore:
    def __init__(self) -> None:
        self.added = None

    def add_chunks(self, doc_id, filename, chunks, embeddings) -> None:
        self.added = (doc_id, filename, chunks, embeddings)


@pytest.mark.asyncio
async def test_ingest_document_parses_chunks_embeds_and_stores(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "doc.txt"
    path.write_text("abcdefghijklmnopqrstuvwxyz", encoding="utf-8")
    store = FakeStore()
    settings = Settings(
        llm=LlmSettings("qwen3:4b", "http://localhost:11434", 0.1, 128),
        embeddings=EmbeddingSettings("nomic-embed-text", "http://localhost:11434"),
        retrieval=RetrievalSettings(chunk_size=10, chunk_overlap=2, top_k=5),
        storage=StorageSettings(tmp_path / "documents", tmp_path / "chroma", "test"),
        server=ServerSettings("127.0.0.1", 8000),
    )

    async def fake_embed(texts, settings):
        return [[float(index)] for index, _ in enumerate(texts)]

    monkeypatch.setattr("backend.ingestion.pipeline.embed", fake_embed)

    chunks = await ingest_document(path, "doc-id", "doc.txt", settings=settings, store=store)

    assert chunks == 3
    assert store.added[0] == "doc-id"
    assert store.added[1] == "doc.txt"
    assert len(store.added[2]) == 3
    assert len(store.added[3]) == 3
