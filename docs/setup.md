# Setup Guide

## Prerequisites

### All platforms

- Python 3.11 recommended
- pip
- ~4 GB free disk space for default models

### Install Ollama

Ollama manages local LLM downloads and serves them over a local HTTP API.

**macOS:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download the app from https://ollama.com/download

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**

Download the installer from https://ollama.com/download/windows and run it.

---

## Step-by-Step Setup

### 1. Clone the repository

```bash
git clone https://github.com/apg6390/myLocalKb.git
cd myLocalKb
```

### 2. Run the setup script

**macOS / Linux:**

```bash
bash setup.sh
```

**Windows (PowerShell):**

```powershell
.\setup.bat
```

This script will:

- Check that Ollama is installed
- Pull `qwen3:4b` (~2.5 GB), which requires internet this one time
- Pull `nomic-embed-text` (~274 MB)
- Install Python dependencies
- Create the `data/` directory structure

### 3. Start the app

For day-to-day startup after setup, see `RUNNING.md` in the project root.

**macOS / Linux:**

```bash
# Start Ollama if not running as a background service
ollama serve &

# Start the application
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Windows (PowerShell):**

```powershell
Start-Process ollama -ArgumentList "serve" -NoNewWindow
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 4. Open the app

Navigate to `http://127.0.0.1:8000` in your browser.

---

## Low-RAM Configuration (< 8 GB RAM)

Edit `config.yaml` before starting:

```yaml
llm:
  model: phi3:mini    # ~2.3 GB, MIT licensed
```

Then pull the smaller model:

```bash
ollama pull phi3:mini
```

---

## Troubleshooting

### "connection refused" to Ollama

Ensure `ollama serve` is running. On macOS/Windows, the Ollama app may start it automatically as a background service.

### Slow first answer

The first query cold-loads the model into memory. Subsequent queries are much faster.

### Port 8000 already in use

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Then open `http://127.0.0.1:8001`.

### "No module named uvicorn"

Install dependencies into the Python environment you are using:

```powershell
python -m pip install -r requirements.txt
```

If your default Python is 3.12 or newer and ChromaDB dependencies fail to install, install Python 3.11 and run:

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### PDF text not extracted

Some scanned PDFs are image-only and have no extractable text. Use a PDF with actual text content.
