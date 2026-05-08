#!/usr/bin/env bash
set -euo pipefail

echo "=== myLocalKb Setup ==="

# Check Ollama
if ! command -v ollama &> /dev/null; then
  echo "ERROR: Ollama is not installed."
  echo "Install it from: https://ollama.com/download"
  exit 1
fi
echo "✓ Ollama found: $(ollama --version)"

# Pull models
echo ""
echo "Pulling qwen3:4b (Apache 2.0, ~2.5 GB)..."
ollama pull qwen3:4b

echo "Pulling nomic-embed-text (Apache 2.0, ~274 MB)..."
ollama pull nomic-embed-text

# Python deps
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Data directories
mkdir -p data/documents data/chroma_db

echo ""
echo "=== Setup complete ==="
echo ""
echo "To start the app:"
echo "  ollama serve &"
echo "  uvicorn backend.main:app --host 127.0.0.1 --port 8000"
echo ""
echo "Then open: http://localhost:8000"
