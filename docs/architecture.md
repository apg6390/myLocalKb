# Architecture

## Overview

myLocalKb is a three-layer application: a vanilla JS frontend, a FastAPI backend, and a local AI stack (Ollama + ChromaDB). All components run on the user's machine. No network calls are made after the initial model download.

```text
Browser (http://127.0.0.1:8000)
|-- Document Upload UI -- POST /api/documents
`-- Chat UI ----------- POST /api/query

FastAPI Backend
|-- Ingestion Pipeline
|   `-- parse -> chunk -> embed -> store
`-- RAG Query Handler
    `-- embed question -> retrieve chunks -> assemble prompt -> call LLM

Local AI/Data Layer
|-- ChromaDB
|   `-- data/chroma_db/
|-- Uploaded documents
|   `-- data/documents/
`-- Ollama
    |-- embed: nomic-embed-text
    `-- chat: qwen3:4b
```

---

## Data Flow

### Document Ingestion

1. User uploads file via browser to `POST /api/documents` as multipart form data.
2. File is saved to `data/documents/<uuid>_<filename>`.
3. Parser extracts text using pypdf, python-docx, python-pptx, or plain text parsing.
4. Chunker splits text into overlapping windows, defaulting to 512 characters with 64 characters of overlap.
5. Each chunk is embedded through local Ollama using `nomic-embed-text`.
6. Chunks, embeddings, and metadata are stored in ChromaDB collection `mylocalkb`.
7. API returns `{id, filename, chunks}`.

### Query

1. User submits a question to `POST /api/query`.
2. Question is embedded through local Ollama using `nomic-embed-text`.
3. ChromaDB cosine similarity search retrieves the top matching chunks.
4. Retrieved chunks are injected into the strict RAG system prompt.
5. Ollama `qwen3:4b` generates an answer.
6. Backend enforces source citation if the model omits it.
7. API returns `{answer, sources}`.

---

## Anti-Hallucination Design

Three layers enforce no-hallucination behavior:

1. **Empty-context short-circuit**: if no chunks are retrieved, the backend returns the canned "not found" message without calling the LLM.
2. **System prompt instruction**: the LLM is explicitly told to answer only from the provided excerpts.
3. **Source enforcement**: the backend appends source filenames from ChromaDB metadata if the LLM omits them.

---

## Key Design Decisions

See `docs/adr/` for full Architecture Decision Records.

| Decision | Choice | Reason |
|---|---|---|
| LLM model | qwen3:4b | Apache 2.0, reliable RAG default for constrained laptop hardware |
| LLM runtime | Ollama | Single binary, cross-platform, manages model downloads |
| Embedding model | nomic-embed-text | Apache 2.0, high quality, available via Ollama |
| Vector store | ChromaDB | In-process, Apache 2.0, persistent |
| PDF parser | pypdf | MIT, pure Python, no system library dependencies |
| Frontend | Vanilla JS | Zero build step, works offline, easy to understand |
| Config | YAML | Human-readable, easy to edit without code changes |
