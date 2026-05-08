# myLocalKb

A fully **offline**, local-only personal knowledge base with a chat interface powered by a local LLM.

Upload your research reports, articles, PDFs, and DOCX files, then ask questions in plain English and get grounded, cited answers. No cloud. No API keys. No data leaves your machine.

![myLocalKb web interface](docs/assets/web-ui-screenshot.png)

---

## Project Status

**Early alpha / local prototype.** The core offline upload, retrieval, and chat flow is working, but the app is still being hardened for broader public use.

---

## Features

- **Document ingestion** - upload PDF, DOCX, PPTX, TXT, and Markdown files via the web UI
- **Semantic search** - documents are chunked and embedded locally using `nomic-embed-text`
- **Chat interface** - ask questions; the LLM answers strictly from your documents
- **No hallucination** - if the answer is not in your knowledge base, the bot says so
- **Source citations** - every answer names the source documents it used
- **100% offline** - works without internet after the one-time model download

---

## Quick Start

### Prerequisites

- Python 3.11 or 3.12 recommended
- [Ollama](https://ollama.com/download) (free, open-source local LLM runtime)

### Setup

```bash
# Clone the repo
git clone https://github.com/apg6390/myLocalKb.git
cd myLocalKb

# Run the setup script (downloads models + installs Python deps)
# macOS / Linux:
bash setup.sh

# Windows (PowerShell):
.\setup.bat
```

### Run

See [RUNNING.md](RUNNING.md) for the quick command reference.

**Windows PowerShell:**

```powershell
cd path\to\myLocalKb

# Window 1
ollama serve

# Window 2
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`.

---

## Hardware Requirements

| Configuration | RAM | Disk |
|---|---|---|
| Default (`qwen3:4b`) | 8 GB | ~3 GB for models |
| Higher quality (`qwen3:8b`) | 16 GB | ~5.5 GB for models |
| Low-RAM (`phi3:mini`) | 4 GB | ~2.5 GB for models |

To use the low-RAM model, edit `config.yaml`:

```yaml
llm:
  model: phi3:mini
```

---

## Adding Documents

1. Open `http://127.0.0.1:8000`
2. Drag and drop files onto the upload zone, or click **Choose Files**
3. Supported formats: `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`
4. The document is processed and indexed in the background; you will see a confirmation when ready

---

## Asking Questions

Type your question in the chat box and press **Send**.

The assistant will:

- Search your knowledge base for relevant passages
- Compose an answer based **only** on what it found
- Show a deduplicated source list below each answer

If nothing relevant is found, it will say: *"I could not find relevant information in the knowledge base."*

---

## Configuration

All settings live in `config.yaml`:

```yaml
llm:
  model: qwen3:4b              # change to qwen3:8b for higher quality
  temperature: 0.1             # lower = more deterministic answers

retrieval:
  chunk_size: 512              # characters per chunk
  chunk_overlap: 64            # overlap between adjacent chunks
  top_k: 5                     # number of chunks retrieved per query
```

---

## Project Structure

```text
myLocalKb/
|-- backend/        Python FastAPI backend
|-- frontend/       HTML/CSS/JS web interface (no build step)
|-- data/           Your documents and vector store (gitignored)
|-- docs/           Architecture notes and setup guide
|-- tests/          pytest test suite
`-- config.yaml     Runtime configuration
```

See `docs/architecture.md` for a full technical overview.
See `RUNNING.md` for day-to-day startup commands.

---

## License

Apache License 2.0 - see [LICENSE](LICENSE).

Third-party dependency and model licenses are documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

## For Developers

See `CLAUDE.md` for AI-assisted development instructions (Claude Code, Codex, etc.).
See `builder_prompt.md` for the original scaffold prompt used to build this project.
