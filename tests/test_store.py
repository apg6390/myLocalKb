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


def test_chroma_store_add_query_list_delete(tmp_path: Path) -> None:
    pytest.importorskip("chromadb")
    from backend.retrieval.store import ChromaStore

    settings = Settings(
        llm=LlmSettings("qwen3:4b", "http://localhost:11434", 0.1, 128),
        embeddings=EmbeddingSettings("nomic-embed-text", "http://localhost:11434"),
        retrieval=RetrievalSettings(512, 64, 5),
        storage=StorageSettings(tmp_path / "documents", tmp_path / "chroma", "test_collection"),
        server=ServerSettings("127.0.0.1", 8000),
    )
    store = ChromaStore(settings)
    chunks = [{"text": "alpha beta", "page": 1, "chunk_index": 0}]
    embeddings = [[0.1, 0.2, 0.3]]

    store.add_chunks("doc-id", "doc.txt", chunks, embeddings)

    documents = store.list_documents()
    assert documents[0]["id"] == "doc-id"
    assert documents[0]["chunks"] == 1
    assert store.query([0.1, 0.2, 0.3], 1)[0]["filename"] == "doc.txt"

    store.delete_document("doc-id")
    assert store.list_documents() == []
