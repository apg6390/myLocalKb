from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import ROOT_DIR, ensure_storage_dirs, get_settings
from backend.retrieval.store import get_store
from backend.routers.documents import router as documents_router
from backend.routers.query import router as query_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="myLocalKb", version="0.1.0")

app.include_router(documents_router, prefix="/api")
app.include_router(query_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    ensure_storage_dirs(settings)
    get_store()
    logger.info("myLocalKb started with model %s", settings.llm.model)


frontend_dir = ROOT_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=Path(frontend_dir), html=True), name="frontend")
