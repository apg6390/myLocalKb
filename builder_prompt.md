# myLocalKb — Builder Prompt

> **Purpose:** This is the canonical prompt given to an AI coding agent (Claude Code, Codex, etc.) to build `myLocalKb` from scratch. Run it in the project root after the scaffold files (`CLAUDE.md`, `AGENTS.md`, `config.yaml`, etc.) are in place.

---

## Prompt

Build a fully offline, local-only personal knowledge base application called **myLocalKb**. The complete spec, architecture decisions, and hard rules are in `CLAUDE.md`. Read `CLAUDE.md` first and follow every instruction in it before writing any code.

---

### What you are building

A local web application where a user can:
1. **Upload documents** (PDF, DOCX, TXT, Markdown) via a web interface.
2. **Chat with their knowledge base** — ask questions in natural language and get grounded answers that cite the source documents.

The system never hallucinations. If retrieved context doesn't answer the question, the bot says so.

---

### LLM Choice (confirmed)

Use **Ollama** as the local LLM runtime.  
Primary model: **`qwen3:4b`** (Apache 2.0 licensed).  
Embedding model: **`nomic-embed-text`** (Apache 2.0 via Ollama).  
Higher-quality option for roomier machines: **`qwen3:8b`** (Apache 2.0 licensed). Fallback for low-RAM machines: **`phi3:mini`** (MIT licensed). Conservative fallback: **`mistral:7b-instruct`** (Apache 2.0 licensed). Expose the selected model via `config.yaml`.

Do NOT use any cloud LLM API (OpenAI, Anthropic, Gemini, Cohere, etc.).

---

### Build steps (in order)

#### Step 1 — Project skeleton
Create the directory structure exactly as defined in `CLAUDE.md`:
- `backend/` with subpackages `ingestion/`, `retrieval/`, `llm/`, `routers/`
- `frontend/` with `index.html`, `style.css`, `app.js`
- `data/documents/` and `data/chroma_db/` (empty, gitignored)
- `docs/` with `architecture.md`, `setup.md`, `adr/001-llm-choice.md`
- `tests/` mirroring `backend/`

#### Step 2 — Configuration
Create `config.yaml`:
```yaml
llm:
  model: qwen3:4b
  base_url: http://localhost:11434
  temperature: 0.1
  max_tokens: 2048

embeddings:
  model: nomic-embed-text
  base_url: http://localhost:11434

retrieval:
  chunk_size: 512
  chunk_overlap: 64
  top_k: 5

storage:
  documents_dir: data/documents
  chroma_dir: data/chroma_db

server:
  host: 127.0.0.1
  port: 8000
```

Create `backend/config.py` that loads this file and exposes a typed `Settings` dataclass.

#### Step 3 — Requirements
Create `requirements.txt` with pinned versions:
```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
chromadb>=0.5.0
pypdf>=4.2.0
python-docx>=1.1.0
python-pptx>=1.0.0
httpx>=0.27.0
python-multipart>=0.0.9
pyyaml>=6.0
```

No LangChain, no sentence-transformers, no OpenAI SDK, no Anthropic SDK.

#### Step 4 — Document ingestion pipeline

`backend/ingestion/parsers.py`:
- `parse_pdf(path) -> list[str]` using pypdf — one string per page
- `parse_docx(path) -> list[str]` using python-docx — one string per paragraph run
- `parse_pptx(path) -> list[str]` using python-pptx — one string per slide, concatenating all text frames and speaker notes for that slide
- `parse_text(path) -> list[str]` for .txt and .md — split on double newlines

`backend/ingestion/chunker.py`:
- `chunk_text(pages: list[str], chunk_size: int, overlap: int) -> list[dict]`
- Returns `[{"text": str, "page": int, "chunk_index": int}]`
- Use a sliding window over character count (not token count — no tokenizer dependency)

`backend/ingestion/pipeline.py`:
- `ingest_document(file_path: Path, doc_id: str, filename: str) -> int`
- Parses → chunks → embeds each chunk via `backend/retrieval/embedder.py` → stores in ChromaDB via `backend/retrieval/store.py`
- Returns number of chunks stored

#### Step 5 — Retrieval layer

`backend/retrieval/embedder.py`:
- `embed(texts: list[str]) -> list[list[float]]`
- Calls `POST http://localhost:11434/api/embed` with `{"model": "nomic-embed-text", "input": texts}`
- Uses `httpx.AsyncClient`

`backend/retrieval/store.py`:
- Wraps ChromaDB `PersistentClient`
- `add_chunks(doc_id, filename, chunks, embeddings)` — upserts with metadata
- `query(embedding, k) -> list[dict]` — returns top-k chunks with `text`, `filename`, `doc_id`, `page`, `distance`
- `delete_document(doc_id)` — removes all chunks for a document
- `list_documents() -> list[dict]` — returns unique documents with chunk counts

#### Step 6 — LLM chat layer

`backend/llm/chat.py`:
- `answer_query(question: str, context_chunks: list[dict]) -> str`
- Assembles the RAG prompt (see system prompt in `CLAUDE.md` — use it verbatim)
- Calls `POST http://localhost:11434/api/chat` with `{"model": ..., "messages": [...], "stream": false}`
- If `context_chunks` is empty, return `"I could not find relevant information in the knowledge base."` without calling the LLM
- Parse the response; if `Sources:` block is missing, append it from `context_chunks` metadata

#### Step 7 — FastAPI routes

`backend/routers/documents.py`:
- `POST /api/documents` — multipart upload, validate extension (`.pdf`, `.docx`, `.pptx`, `.txt`, `.md`), save to `data/documents/<uuid>_<filename>`, call `ingest_document`, return `{"id", "filename", "chunks"}`
- `GET /api/documents` — return list from `store.list_documents()`
- `DELETE /api/documents/{doc_id}` — call `store.delete_document`, delete file from disk

`backend/routers/query.py`:
- `POST /api/query` — body `{"question": str, "k": int = 5}`, embed question, retrieve chunks, call `answer_query`, return `{"answer": str, "sources": list[str]}`

`backend/main.py`:
- Mount `frontend/` as static files at `/`
- Include both routers with prefix `/api`
- On startup, ensure ChromaDB collection exists

#### Step 8 — Frontend

`frontend/index.html`:
- Two-panel layout: left sidebar for document list + upload, right panel for chat
- Document upload: drag-and-drop zone + file picker button
- Chat: message thread, input box, send button
- Show a "Sources:" section below each bot answer with clickable document names

`frontend/style.css`:
- Clean, minimal, dark theme
- Responsive down to 768px
- No external fonts or CDN links (everything inline or from system fonts)

`frontend/app.js`:
- `uploadDocument(file)` → calls `POST /api/documents`
- `loadDocuments()` → calls `GET /api/documents`, renders sidebar list
- `deleteDocument(id)` → calls `DELETE /api/documents/{id}`
- `sendQuery(question)` → calls `POST /api/query`, appends answer + sources to chat
- Show a spinner while waiting for LLM response
- Disable send button while a query is in flight

#### Step 9 — Tests

Write pytest tests in `tests/`:
- `test_parsers.py` — test each parser (PDF, DOCX, PPTX, TXT) with a small fixture file; for PPTX verify that slide text and speaker notes are both extracted
- `test_chunker.py` — test sliding window, overlap, edge cases
- `test_store.py` — test add, query, delete with a temp ChromaDB directory
- `test_pipeline.py` — integration test: ingest a small PDF and a small PPTX, verify chunk count
- `test_chat.py` — mock the Ollama HTTP call, verify source citation enforcement

#### Step 10 — Setup scripts

`setup.sh` (Unix/macOS):
```bash
#!/usr/bin/env bash
set -e
echo "Checking Ollama..."
which ollama || { echo "Install Ollama from https://ollama.com/download"; exit 1; }
ollama pull qwen3:4b
ollama pull nomic-embed-text
pip install -r requirements.txt
mkdir -p data/documents data/chroma_db
echo "Setup complete. Run: uvicorn backend.main:app --host 127.0.0.1 --port 8000"
```

`setup.bat` (Windows):
- Equivalent PowerShell/batch steps

#### Step 11 — Documentation

`docs/setup.md` — complete install guide for macOS, Linux, Windows  
`docs/architecture.md` — data flow diagram (text/ASCII), component descriptions  
`docs/adr/001-llm-choice.md` — ADR documenting the Qwen3 + Ollama decision

#### Step 12 — Final verification

After writing all code:
1. Verify no file imports `openai`, `anthropic`, `langchain`, `cohere`, `boto3`, or any other cloud SDK.
2. Verify the system prompt in `chat.py` exactly matches `CLAUDE.md`.
3. Verify `data/` is in `.gitignore` and no binary model files exist in the repo.
4. Run `pytest tests/ -v` — all tests must pass.
5. Start the server and confirm the frontend loads at `http://localhost:8000`.

---

### Definition of done

- [ ] `uvicorn backend.main:app` starts without errors
- [ ] User can upload a PDF, DOCX, or TXT file via the UI
- [ ] User can ask a question and receive an answer citing document names
- [ ] If the knowledge base has no relevant info, the bot says so explicitly
- [ ] `pytest tests/ -v` passes
- [ ] No cloud dependencies anywhere in the code
- [ ] `THIRD_PARTY_LICENSES.md` lists all dependencies and their licenses
