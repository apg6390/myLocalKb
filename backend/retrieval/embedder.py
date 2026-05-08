from __future__ import annotations

import logging

import httpx

from backend.config import EmbeddingSettings, get_settings


logger = logging.getLogger(__name__)


async def embed(texts: list[str], settings: EmbeddingSettings | None = None) -> list[list[float]]:
    if not texts:
        return []

    resolved = settings or get_settings().embeddings
    payload = {"model": resolved.model, "input": texts}

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{resolved.base_url}/api/embed", json=payload)
        response.raise_for_status()
        data = response.json()

    embeddings = data.get("embeddings")
    if embeddings is None and "embedding" in data:
        embeddings = [data["embedding"]]

    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        logger.error("Unexpected Ollama embedding response: %s", data)
        raise RuntimeError("Ollama returned an unexpected embedding response")

    return embeddings
