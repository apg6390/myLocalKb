# myLocalKb — Claude Code Instructions

## Project Overview

**myLocalKb** is a fully offline, local-only personal knowledge base with a chat interface powered by a local LLM. Users upload documents (PDF, DOCX, PPTX, TXT, MD) which are chunked and embedded into a local vector store. A chat interface lets users query their knowledge base; the LLM grounds every answer strictly in retrieved document chunks — no hallucination allowed.

Inspired by [PageIndex](https://github.com/VectifyAI/PageIndex) and [OpenKB](https://github.com/VectifyAI/OpenKB), but **100% offline — no cloud, no API keys, no telemetry**.

---

## Hard Rules (never violate)

1. **No network calls at runtime.** All models, embeddings, and data stay on the local machine.
2. **No hallucination.** The LLM must refuse to answer if the retrieved context is insufficient; it must cite source document names in every answer.
3. **Apache 2.0 project license.** All new code must be compatible. See `THIRD_PARTY_LICENSES.md` before adding dependencies.
4. **No model weights in the repo.** Models are pulled via Ollama at setup time (see `docs/setup.md`).
5. **No cloud-dependent libraries** (no OpenAI SDK, no Anthropic SDK, no LangChain cloud features, no Pinecone, no Weaviate cloud, etc.).

---

## Chosen Tech Stack

| Layer | Choice | License | Why |
|---|---|---|---|
| LLM runtime | [Ollama](https://ollama.com) | MIT | Single binary, manages model downloads, exposes local REST API |
| Chat LLM | `qwen3:4b` | Apache 2.0 | Reliable local RAG default for constrained laptop hardware |
| Fallback LLM | `phi3:mini` | MIT | For machines with < 8 GB RAM |
| Embeddings | `nomic-embed-text` via Ollama | Apache 2.0 | High-quality local embeddings, no extra install |
| Vector store | [ChromaDB](https://www.trychroma.com) | Apache 2.0 | In-process, persistent, no separate server |
| Backend | FastAPI + Uvicorn | MIT / BSD | Async, typed, minimal |
| PDF parsing | pypdf | MIT | Pure-Python, no system libs |
| DOCX parsing | python-docx | MIT | Standard library |
| PPTX parsing | python-pptx | MIT | Extracts text from slides and speaker notes |
| Frontend | Vanilla HTML/CSS/JS | — | Zero build step, works offline |

> **LLM Rationale:** `qwen3:4b` (Apache 2.0) is the default local chat model for RAG because reliability on a 16 GB laptop matters more than peak answer quality. It stays comfortably within the offline Ollama workflow while leaving headroom for FastAPI, ChromaDB, the browser, and the OS. Users with more headroom can switch to `qwen3:8b`; users with less RAM should switch to `phi3:mini` (MIT, ~2.3 GB). `mistral:7b-instruct` remains an acceptable conservative fallback. The `config.yaml` exposes the model setting for this.

---

## Project Structure

```
myLocalKb/
├── CLAUDE.md                  ← you are here (AI dev instructions)
├── AGENTS.md                  ← Codex / other agent instructions
├── README.md                  ← end-user readme
├── LICENSE                    ← Apache 2.0
├── THIRD_PARTY_LICENSES.md    ← dependency + model license acknowledgments
├── builder_prompt.md          ← the original prompt used to scaffold this project
├── .gitignore
├── config.yaml                ← runtime config (LLM model, chunk size, etc.)
├── requirements.txt           ← Python deps (pinned)
├── setup.sh                   ← Unix setup script
├── setup.bat                  ← Windows setup script
│
├── backend/
│   ├── main.py                ← FastAPI app entry point
│   ├── config.py              ← loads config.yaml
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pipeline.py        ← orchestrates ingest: parse → chunk → embed → store
│   │   ├── parsers.py         ← PDF, DOCX, TXT, MD parsers
│   │   └── chunker.py         ← recursive text splitter
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── store.py           ← ChromaDB wrapper (add, query, delete)
│   │   └── embedder.py        ← Ollama nomic-embed-text wrapper
│   ├── llm/
│   │   ├── __init__.py
│   │   └── chat.py            ← Ollama chat wrapper + RAG prompt assembly
│   └── routers/
│       ├── __init__.py
│       ├── documents.py       ← POST /api/documents, GET /api/documents
│       └── query.py           ← POST /api/query
│
├── frontend/
│   ├── index.html             ← single-page app shell
│   ├── style.css
│   └── app.js                 ← chat UI + document upload UI
│
├── data/
│   ├── documents/             ← original uploaded files (gitignored)
│   └── chroma_db/             ← vector store (gitignored)
│
└── docs/
    ├── architecture.md        ← design decisions
    ├── setup.md               ← step-by-step install guide
    └── adr/                   ← architecture decision records
        └── 001-llm-choice.md
```

---

## Key Behaviours to Maintain

### RAG Pipeline
1. On upload, documents are parsed → split into overlapping chunks (default 512 tokens, 64 overlap) → embedded via `nomic-embed-text` → stored in ChromaDB with metadata `{filename, chunk_index, page_number}`.
2. On query, top-k chunks (default k=5) are retrieved → injected into the LLM system prompt → LLM answers **only** using those chunks.

### Anti-Hallucination System Prompt
The LLM system prompt **must** include:
```
You are a research assistant. Answer ONLY using the provided document excerpts.
If the excerpts do not contain enough information to answer the question, respond with:
"I could not find relevant information in the knowledge base."
Always end your answer with a "Sources:" section listing the filenames you used.
```
This wording must **never be removed or weakened**.

### Source Citation
Every answer from the LLM must end with a `Sources:` block listing document filenames. The backend enforces this by parsing the LLM output and appending structured source metadata from ChromaDB if the LLM omits it.

---

## Development Conventions

- **Python 3.11+**. Use type hints everywhere.
- **Async FastAPI**. All route handlers must be `async def`.
- **No global state** in route handlers — use FastAPI dependency injection.
- **Config via `config.yaml`** — never hardcode model names, paths, or parameters.
- **Tests live in `tests/`** (pytest). Each module in `backend/` has a corresponding test file.
- Logging via Python's `logging` module, not `print`.
- All user-uploaded files stored under `data/documents/` with a UUID prefix to avoid collisions.

---

## Adding New Features — Checklist

- [ ] Does it require network access? If yes, reject it.
- [ ] Does it add a new dependency? Check license compatibility with Apache 2.0 and update `THIRD_PARTY_LICENSES.md`.
- [ ] Does it touch the RAG prompt? Verify anti-hallucination rules still hold.
- [ ] Does it store data? Ensure it goes under `data/` and is gitignored.
- [ ] Write or update tests.

---

## Common Tasks

### Run the app (after setup)
```bash
ollama serve &          # start Ollama daemon if not running
cd myLocalKb
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
# open http://localhost:8000
```

### Pull required Ollama models
```bash
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

### Run tests
```bash
pytest tests/ -v
```

### Add a new document parser
1. Add a parser function in `backend/ingestion/parsers.py` following the signature `parse_<format>(path: Path) -> list[str]`.
2. Register it in the `PARSERS` dict in `pipeline.py`.
3. Add the file extension to `ALLOWED_EXTENSIONS` in `routers/documents.py`.
4. Add a test in `tests/test_parsers.py`.
