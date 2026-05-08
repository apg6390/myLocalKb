# Architecture

## Overview

myLocalKb is a three-layer application: a vanilla JS frontend, a FastAPI backend, and a local AI stack (Ollama + ChromaDB). All components run on the user's machine. No network calls after initial model download.

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (localhost:8000)              │
│  ┌──────────────────────┐   ┌──────────────────────────┐   │
│  │   Document Upload UI  │   │       Chat UI             │   │
│  └──────────┬───────────┘   └────────────┬─────────────┘   │
└─────────────┼────────────────────────────┼─────────────────-┘
              │ POST /api/documents         │ POST /api/query
              ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                                                              │
│  ┌─────────────────────┐    ┌──────────────────────────┐   │
│  │  Ingestion Pipeline  │    │      RAG Query Handler    │   │
│  │                      │    │                          │   │
│  │  parse → chunk →     │    │  embed question →        │   │
│  │  embed → store       │    │  retrieve chunks →       │   │
│  └─────────┬────────────┘    │  assemble prompt →       │   │
│            │                 │  call LLM → return answer│   │
│            │                 └──────────────────────────┘   │
└────────────┼───────────────────────────────┬────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│       ChromaDB          │    │        Ollama (local)         │
│  (persistent on disk)   │    │                              │
│                         │◄───│  embed: nomic-embed-text     │
│  - document chunks      │    │  chat:  qwen3:4b             │
│  - embeddings           │    │                              │
│  - metadata             │    │  HTTP API: localhost:11434   │
└────────────────────────┘    └──────────────────────────────┘
             │
             ▼
┌────────────────────────┐
│   data/chroma_db/       │
│   data/documents/       │
│   (local filesystem)    │
└────────────────────────┘
```

---

## Data Flow

### Document Ingestion

1. User uploads file via browser → `POST /api/documents` (multipart)
2. File saved to `data/documents/<uuid>_<filename>`
3. Parser extracts text (pypdf / python-docx / plain text)
4. Chunker splits text into overlapping windows (~512 chars, 64 overlap)
5. Each chunk embedded via Ollama `nomic-embed-text` → 768-dim float vector
6. Chunks + embeddings + metadata stored in ChromaDB collection `mylocalkb`
7. Response: `{id, filename, chunks}`

### Query

1. User types question → `POST /api/query`
2. Question embedded via Ollama `nomic-embed-text`
3. ChromaDB cosine similarity search → top-5 chunks retrieved
4. If no chunks found (distance > threshold) → return "not found" immediately
5. Chunks injected into LLM system prompt with anti-hallucination instructions
6. Ollama `qwen3:4b` generates answer
7. Backend parses answer for `Sources:` block; appends from metadata if missing
8. Response: `{answer, sources: [filename, ...]}`

---

## Anti-Hallucination Design

Three layers enforce no-hallucination:

1. **Empty-context short-circuit**: if ChromaDB returns no chunks above the similarity threshold, the backend returns the canned "not found" message without calling the LLM at all.
2. **System prompt instruction**: the LLM is explicitly told to answer only from the provided excerpts.
3. **Source enforcement**: the backend always appends source filenames from ChromaDB metadata, regardless of what the LLM generates.

---

## Key Design Decisions

See `docs/adr/` for full Architecture Decision Records.

| Decision | Choice | Reason |
|---|---|---|
| LLM model | qwen3:4b | Apache 2.0, reliable RAG default for constrained laptop hardware |
| LLM runtime | Ollama | Single binary, cross-platform, manages GGUF quantisation |
| Embedding model | nomic-embed-text | Apache 2.0, high quality, available via Ollama |
| Vector store | ChromaDB | In-process (no server), Apache 2.0, persistent |
| PDF parser | pypdf | MIT, pure Python, no system library dependencies |
| Frontend | Vanilla JS | Zero build step, works offline, easy to understand |
| Config | YAML | Human-readable, easy to edit without code changes |
