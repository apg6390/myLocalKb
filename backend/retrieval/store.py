from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from backend.config import Settings, ensure_storage_dirs, get_settings
from backend.ingestion.chunker import Chunk


class ChromaStore:
    def __init__(self, settings: Settings | None = None) -> None:
        import chromadb

        self.settings = settings or get_settings()
        ensure_storage_dirs(self.settings)
        self.client = chromadb.PersistentClient(path=str(self.settings.storage.chroma_dir))
        self.collection = self.client.get_or_create_collection(
            name=self.settings.storage.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        doc_id: str,
        filename: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")

        ingested_at = datetime.now(timezone.utc).isoformat()
        ids = [f"{doc_id}:{chunk['chunk_index']}" for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "filename": filename,
                "page": int(chunk["page"]),
                "chunk_index": int(chunk["chunk_index"]),
                "ingested_at": ingested_at,
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, embedding: list[float], k: int) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=max(1, k),
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks: list[dict[str, Any]] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            metadata = metadata or {}
            chunks.append(
                {
                    "text": text,
                    "filename": metadata.get("filename", ""),
                    "doc_id": metadata.get("doc_id", ""),
                    "page": metadata.get("page"),
                    "chunk_index": metadata.get("chunk_index"),
                    "distance": distance,
                }
            )
        return chunks

    def delete_document(self, doc_id: str) -> None:
        self.collection.delete(where={"doc_id": doc_id})

    def list_documents(self) -> list[dict[str, Any]]:
        result = self.collection.get(include=["metadatas"])
        documents: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"id": "", "filename": "", "ingested_at": "", "chunks": 0}
        )

        for metadata in result.get("metadatas", []):
            if not metadata:
                continue
            doc_id = str(metadata.get("doc_id", ""))
            if not doc_id:
                continue
            record = documents[doc_id]
            record["id"] = doc_id
            record["filename"] = metadata.get("filename", "")
            record["ingested_at"] = metadata.get("ingested_at", "")
            record["chunks"] += 1

        return sorted(documents.values(), key=lambda item: str(item["ingested_at"]), reverse=True)


_store: ChromaStore | None = None


def get_store() -> ChromaStore:
    global _store
    if _store is None:
        _store = ChromaStore()
    return _store
