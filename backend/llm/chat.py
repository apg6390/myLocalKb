from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from backend.config import LlmSettings, get_settings


logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = "I could not find relevant information in the knowledge base."

RAG_SYSTEM_PROMPT = """You are a research assistant. Answer ONLY using the provided document excerpts.
If the excerpts do not contain enough information to answer the question, respond with:
"I could not find relevant information in the knowledge base."
Always end your answer with a "Sources:" section listing the filenames you used."""


def _format_context(context_chunks: list[dict[str, Any]]) -> str:
    excerpts: list[str] = []
    for index, chunk in enumerate(context_chunks, start=1):
        filename = chunk.get("filename", "unknown")
        page = chunk.get("page", "unknown")
        text = chunk.get("text", "")
        excerpts.append(f"[{index}] Source: {filename}, page {page}\n{text}")
    return "\n\n".join(excerpts)


def _source_names(context_chunks: list[dict[str, Any]]) -> list[str]:
    names = []
    for chunk in context_chunks:
        filename = str(chunk.get("filename", "")).strip()
        if filename and filename not in names:
            names.append(filename)
    return names


def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def ensure_sources(answer: str, context_chunks: list[dict[str, Any]]) -> str:
    sources = _source_names(context_chunks)
    if not sources:
        return answer

    if "Sources:" in answer:
        return answer.strip()

    source_lines = "\n".join(f"- {source}" for source in sources)
    return f"{answer.strip()}\n\nSources:\n{source_lines}"


async def answer_query(
    question: str,
    context_chunks: list[dict[str, Any]],
    settings: LlmSettings | None = None,
) -> str:
    if not context_chunks:
        return NOT_FOUND_MESSAGE

    resolved = settings or get_settings().llm
    context = _format_context(context_chunks)
    messages = [
        {"role": "system", "content": f"{RAG_SYSTEM_PROMPT}\n\nDocument excerpts:\n{context}"},
        {"role": "user", "content": question},
    ]
    payload = {
        "model": resolved.model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": resolved.temperature,
            "num_predict": resolved.max_tokens,
        },
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(f"{resolved.base_url}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        answer = str(data["message"]["content"])
    except KeyError as exc:
        logger.error("Unexpected Ollama chat response: %s", data)
        raise RuntimeError("Ollama returned an unexpected chat response") from exc

    return ensure_sources(_strip_thinking(answer), context_chunks)
