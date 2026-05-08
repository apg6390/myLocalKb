# myLocalKb — AI Agent Instructions (Codex / OpenAI Agents / Generic)

This file is read by AI coding agents (GitHub Copilot, Codex, Cursor, etc.).  
For Claude Code, the canonical instructions are in `CLAUDE.md`.

---

## What This Project Is

**myLocalKb** is a fully offline personal knowledge base with:
- A FastAPI backend that ingests documents (PDF, DOCX, PPTX, TXT, MD) and stores them as vector embeddings in ChromaDB.
- An Ollama-powered local LLM (`qwen3:4b`, Apache 2.0) for answering queries grounded strictly in retrieved document chunks.
- A vanilla HTML/CSS/JS frontend (no build step required).

**It must remain 100% offline** — no cloud APIs, no external services, no network calls at runtime.

---

## Absolute Constraints

1. Never introduce dependencies that phone home, require API keys, or transmit data off-device.
2. Never modify the anti-hallucination system prompt in `backend/llm/chat.py` to be less strict.
3. Never commit model weights or large binary files. Models are managed via Ollama outside the repo.
4. All new Python dependencies must be Apache 2.0, MIT, BSD-2, BSD-3, or ISC licensed. Update `THIRD_PARTY_LICENSES.md` if you add one.
5. `data/` directory contents are gitignored. Never change this.

---

## Tech Stack Summary

- **Runtime**: Python 3.11+, FastAPI, Uvicorn
- **LLM**: Ollama (`qwen3:4b` by default, configurable in `config.yaml`)
- **Embeddings**: Ollama (`nomic-embed-text`)
- **Vector store**: ChromaDB (persistent, in-process)
- **Parsers**: pypdf (PDF), python-docx (DOCX), python-pptx (PPTX), built-ins (TXT/MD)
- **Frontend**: Vanilla JS — no frameworks, no bundler

---

## Repository Layout

```
backend/
  main.py           FastAPI app, mounts frontend static files
  config.py         Reads config.yaml
  ingestion/        parse → chunk → embed → store pipeline
  retrieval/        ChromaDB wrapper + Ollama embedder
  llm/              Ollama chat wrapper + RAG prompt
  routers/          /api/documents and /api/query endpoints
frontend/           index.html, style.css, app.js
data/               gitignored runtime data (uploads + vector store)
docs/               architecture notes, ADRs, setup guide
tests/              pytest test suite
config.yaml         runtime configuration
```

---

## API Contract

### POST `/api/documents`
- Multipart form upload, field name `file`
- Accepts: `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`
- Returns: `{"id": "<uuid>", "filename": "<name>", "chunks": <int>}`

### GET `/api/documents`
- Returns list of all ingested documents: `[{"id", "filename", "ingested_at", "chunks"}]`

### DELETE `/api/documents/{id}`
- Removes document and all its chunks from the vector store

### POST `/api/query`
- Body: `{"question": "<string>", "k": 5}`
- Returns: `{"answer": "<string>", "sources": ["<filename>", ...]}`

---

## Coding Standards

- Type-hint all function signatures.
- Use `async def` for all FastAPI route handlers.
- Config values (model names, chunk size, top-k) come from `config.yaml` via `backend/config.py`.
- Log with `logging`, not `print`.
- Tests in `tests/` mirror the `backend/` structure.

---

## The RAG Prompt (do not weaken)

The system prompt passed to the LLM must contain:
```
You are a research assistant. Answer ONLY using the provided document excerpts.
If the excerpts do not contain enough information to answer the question, respond with:
"I could not find relevant information in the knowledge base."
Always end your answer with a "Sources:" section listing the filenames you used.
```

---

## Setup Commands (for agent context)

```bash
# Install Ollama: https://ollama.com/download  (one-time, system-level)
ollama pull qwen3:4b
ollama pull nomic-embed-text

pip install -r requirements.txt

# Run
ollama serve &
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
