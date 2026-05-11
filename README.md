# myLocalKb

myLocalKb is an offline, local-first personal knowledge base with document upload, local vector search, and an Ollama-powered RAG chat interface.

Upload documents, index them locally, and ask grounded questions against your own files. The app uses local embeddings, a local ChromaDB vector store, and a local LLM served by Ollama.

No cloud LLM APIs are used. No API keys are required. Uploaded documents, embeddings, and vector indexes stay on your machine.

![myLocalKb web interface](docs/assets/web-ui-screenshot.png)

---

## Project Status

**Early alpha / local prototype.** The core offline upload, retrieval, and chat flow works, but the project is still being hardened. Expect rough edges around installation environments, parser quality, scanned PDFs, and large-document performance.

This repository is public so others can inspect, run, fork, and build on the local-first RAG approach.

---

## What Works Today

- Upload and index `.pdf`, `.docx`, `.pptx`, `.txt`, and `.md` files
- Store uploaded files and vector data locally under `data/`
- Generate embeddings locally through Ollama
- Retrieve relevant chunks with ChromaDB
- Answer questions with a local Ollama chat model
- Return source filenames with answers
- Refuse answers when retrieved context is insufficient
- Run the frontend without a JavaScript build step

---

## Why This Exists

Many RAG-style knowledge-base tools rely on hosted LLMs, hosted embedding APIs, telemetry, or managed vector databases. myLocalKb is intentionally small and local:

- FastAPI backend
- Vanilla HTML/CSS/JS frontend
- Ollama for chat and embeddings
- ChromaDB for local vector storage
- Plain file upload workflow
- No cloud API dependency at runtime

---

## Privacy And Offline Model

After the one-time dependency/model setup:

- The app runs on `127.0.0.1`
- Documents are stored under `data/documents/`
- Vector data is stored under `data/chroma_db/`
- Ollama serves models locally through `localhost:11434`
- No OpenAI, Anthropic, Gemini, Cohere, Pinecone, Weaviate Cloud, or other cloud SDK is used

Model downloads are handled by Ollama during setup. Model weights are not stored in this repository.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI, Uvicorn |
| Frontend | Vanilla HTML/CSS/JS |
| Chat LLM | `qwen3:4b` via Ollama |
| Embeddings | `nomic-embed-text` via Ollama |
| Vector store | ChromaDB persistent local store |
| Parsers | pypdf, python-docx, python-pptx, built-in text parsing |
| Tests | pytest, pytest-asyncio |

---

## Quick Start

### Prerequisites

- Python 3.11 or 3.12 recommended
- [Ollama](https://ollama.com/download)
- About 4 GB free disk space for the default models

### Clone

```bash
git clone https://github.com/apg6390/myLocalKb.git
cd myLocalKb
```

### Setup

macOS / Linux:

```bash
bash setup.sh
```

Windows PowerShell:

```powershell
.\setup.bat
```

The setup script installs Python dependencies and pulls:

- `qwen3:4b`
- `nomic-embed-text`

### Run

See [RUNNING.md](RUNNING.md) for day-to-day startup commands.

In one terminal:

```bash
ollama serve
```

In another terminal:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

---

## Hardware Requirements

| Configuration | RAM | Disk |
|---|---:|---:|
| Default (`qwen3:4b`) | 8 GB | ~3 GB for models |
| Higher quality (`qwen3:8b`) | 16 GB | ~5.5 GB for models |
| Low-RAM (`phi3:mini`) | 4 GB | ~2.5 GB for models |

To switch models, edit `config.yaml`:

```yaml
llm:
  model: qwen3:8b
```

Then pull the selected model:

```bash
ollama pull qwen3:8b
```

---

## Usage

### Add Documents

1. Open `http://127.0.0.1:8000`
2. Drag and drop a supported file, or click the upload area
3. Wait for the upload/indexing status to complete
4. Confirm the document appears in the sidebar

Supported formats:

- `.pdf`
- `.docx`
- `.pptx`
- `.txt`
- `.md`

### Ask Questions

Type a question into the chat input and press **Send**.

The assistant will:

1. Embed the question locally
2. Retrieve relevant chunks from ChromaDB
3. Ask the local LLM to answer only from those chunks
4. Show source filenames below the answer

If the retrieved context is insufficient, it should respond:

```text
I could not find relevant information in the knowledge base.
```

---

## API Summary

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/documents` | Upload and index a document |
| `GET` | `/api/documents` | List indexed documents |
| `DELETE` | `/api/documents/{id}` | Delete a document and its chunks |
| `POST` | `/api/query` | Ask a question against indexed documents |

See [docs/architecture.md](docs/architecture.md) for the data flow.

---

## Anti-Hallucination Behavior

The LLM prompt requires answers to use only retrieved excerpts. The backend also enforces source metadata. This does not make the system perfect, but it gives the app a conservative default behavior:

- Empty context returns a fixed "not found" response
- The model is instructed to answer only from excerpts
- Source filenames are returned separately by the API
- The UI deduplicates displayed source names

---

## Configuration

All runtime settings live in `config.yaml`:

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
```

---

## Development

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest tests -v
```

The repository includes a GitHub Actions workflow at [.github/workflows/tests.yml](.github/workflows/tests.yml).

### Contributing / Forking

This is an early local-first RAG project. Useful areas to explore:

- Better document parsing and layout preservation
- OCR support for scanned PDFs
- More file types, such as CSV, XLSX, HTML, or EPUB
- Improved chunking strategies
- Better relevance filtering and retrieval scoring
- Import/export for indexes
- More robust UI states and accessibility checks
- Packaging for easier local installation

Keep changes aligned with the local-only constraint: no runtime cloud APIs, no telemetry, no model weights in the repo, and no dependencies that require user data to leave the machine.

---

## Project Structure

```text
myLocalKb/
|-- backend/        Python FastAPI backend
|-- frontend/       HTML/CSS/JS web interface
|-- data/           Runtime documents and vector DB, gitignored
|-- docs/           Architecture notes and setup guide
|-- tests/          pytest test suite
|-- RUNNING.md      Day-to-day startup guide
|-- config.yaml     Runtime configuration
`-- requirements.txt
```

---

## Known Limitations

- This is an early alpha, not a production-grade document management system.
- OCR for scanned/image-only PDFs is not implemented.
- Parser quality varies by file type and document layout.
- Very large documents may take time to parse, embed, and store.
- Model quality depends on the selected Ollama model and local hardware.
- The app is designed for single-user local use, not multi-user hosting.

---

## Legal And Attribution Notes

- Project code is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
- Third-party Python dependencies, tools, and model references are documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
- Ollama is not bundled with this repository. Users install it separately.
- Model weights are not redistributed in this repository. Users download models through Ollama and are responsible for complying with each model's license.
- Uploaded documents are user-provided content. Users are responsible for ensuring they have the right to process and store the files they upload.
- The included screenshot is for project demonstration only. Do not publish screenshots containing third-party document excerpts unless you have the right to share them.

---

## Related Documentation

- [Running the app](RUNNING.md)
- [Setup guide](docs/setup.md)
- [Architecture](docs/architecture.md)
- [LLM choice ADR](docs/adr/001-llm-choice.md)
- [Third-party licenses](THIRD_PARTY_LICENSES.md)
