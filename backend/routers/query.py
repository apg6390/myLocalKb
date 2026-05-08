from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.config import Settings, get_settings
from backend.llm.chat import answer_query
from backend.retrieval.embedder import embed
from backend.retrieval.store import ChromaStore, get_store


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int | None = Field(default=None, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


def _sources(chunks: list[dict[str, object]]) -> list[str]:
    sources: list[str] = []
    for chunk in chunks:
        filename = str(chunk.get("filename", "")).strip()
        if filename and filename not in sources:
            sources.append(filename)
    return sources


@router.post("", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    settings: Settings = Depends(get_settings),
    store: ChromaStore = Depends(get_store),
) -> QueryResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty")

    try:
        question_embedding = (await embed([question], settings.embeddings))[0]
        chunks = store.query(question_embedding, request.k or settings.retrieval.top_k)
        answer = await answer_query(question, chunks, settings.llm)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to answer query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer query: {exc}",
        ) from exc

    return QueryResponse(answer=answer, sources=_sources(chunks))
