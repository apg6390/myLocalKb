from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from backend.config import Settings, ensure_storage_dirs, get_settings
from backend.ingestion.pipeline import PARSERS, ingest_document
from backend.retrieval.store import ChromaStore, get_store


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = set(PARSERS.keys())


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    return name or "document"


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    store: ChromaStore = Depends(get_store),
) -> dict[str, object]:
    filename = _safe_filename(file.filename or "")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    ensure_storage_dirs(settings)
    doc_id = str(uuid.uuid4())
    destination = settings.storage.documents_dir / f"{doc_id}_{filename}"

    try:
        content = await file.read()
        destination.write_bytes(content)
        chunks = await ingest_document(destination, doc_id, filename, settings=settings, store=store)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to ingest uploaded document")
        if destination.exists():
            destination.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {exc}",
        ) from exc
    finally:
        await file.close()

    return {"id": doc_id, "filename": filename, "chunks": chunks}


@router.get("")
async def list_documents(store: ChromaStore = Depends(get_store)) -> list[dict[str, object]]:
    return store.list_documents()


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    settings: Settings = Depends(get_settings),
    store: ChromaStore = Depends(get_store),
) -> None:
    store.delete_document(doc_id)
    for path in settings.storage.documents_dir.glob(f"{doc_id}_*"):
        if path.is_file():
            path.unlink()
