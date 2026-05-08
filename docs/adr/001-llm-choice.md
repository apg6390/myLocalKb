# ADR 001 - Local LLM and Embedding Model Selection

**Date:** 2026-05-08
**Status:** Accepted

---

## Context

myLocalKb must run fully offline. We need:
1. A **chat LLM** to generate grounded answers from retrieved document chunks
2. An **embedding model** to convert text to vectors for semantic search
3. A **runtime** to serve both locally

All choices must be compatible with an **Apache 2.0** project license and must not require any cloud service at runtime.

---

## Decision

### LLM Runtime: Ollama (MIT)

Ollama provides a single cross-platform binary that downloads, quantizes (GGUF), and serves models via a local HTTP API (`localhost:11434`). It handles memory management and GPU acceleration automatically. Alternative runtimes considered:
- `llama.cpp` (MIT) - lower-level, requires manual GGUF download and CLI management
- `vllm` (Apache 2.0) - server-grade, overkill for a single-user laptop app
- `llamafile` (Apache 2.0) - single-file executable, less ecosystem support

Ollama wins on ease of use and cross-platform support.

### Chat LLM: `qwen3:4b` (Apache 2.0)

The primary requirement was **Apache 2.0 licensing** at the model level, making the entire stack uniformly permissive. The default also needs to run through Ollama without cloud APIs and run reliably on constrained laptop hardware while FastAPI, ChromaDB, a browser, and the OS are active.

Models evaluated:

| Model | License | RAG Quality | RAM (Q4) | Notes |
|---|---|---|---|---|
| qwen3:4b | Apache 2.0 | Good | ~2.5 GB | Default; reliability-first choice for constrained laptops |
| qwen3:8b | Apache 2.0 | Strong | ~5.2 GB | Higher-quality option for machines with more headroom |
| mistral:7b-instruct | Apache 2.0 | Strong | ~5.5 GB | Conservative fallback; older baseline |
| llama3.1:8b | Meta Llama 3.1 Community | Strong | ~5.8 GB | Not Apache 2.0 |
| llama3.2:3b | Meta Llama 3.2 Community | Moderate | ~2.4 GB | Not Apache 2.0 |
| gemma2:9b | Gemma Terms | Strong | ~6.5 GB | Gemma license is restrictive |
| qwen2.5:7b | Apache 2.0 | Strong | ~5.5 GB | Older strong alternative |
| phi3:mini | MIT | Moderate | ~2.3 GB | Fallback for low-RAM |

`qwen3:4b` is selected as the default. It is Apache 2.0 licensed, available through Ollama, and leaves more RAM/VRAM headroom for the rest of the app on a 16 GB laptop. This is the reliability-first choice for local RAG. Users who prefer better answer quality and can tolerate higher resource use can switch to `qwen3:8b` in `config.yaml`.

`phi3:mini` is offered as a configurable fallback for users with less than 8 GB RAM. `mistral:7b-instruct` remains an acceptable conservative fallback if a user prefers the original Mistral baseline.

### Embedding Model: `nomic-embed-text` (Apache 2.0) via Ollama

Embedding models evaluated:

| Model | License | Dimensions | Quality | Notes |
|---|---|---|---|---|
| nomic-embed-text | Apache 2.0 | 768 | Strong | Available via Ollama, no extra install |
| qwen3-embedding:0.6b | Apache 2.0 | Up to 1024 | Strong | Better modern retrieval option, larger download |
| BAAI/bge-small-en-v1.5 | MIT | 384 | Strong | Requires sentence-transformers install |
| all-MiniLM-L6-v2 | Apache 2.0 | 384 | Moderate | Widely used, smaller |
| text-embedding-nomic-embed-text-v1.5 | Apache 2.0 | 768 | Strong | Same model |

`nomic-embed-text` is selected because it:
- Is available via Ollama as a small single-runtime dependency
- Is Apache 2.0 licensed
- Produces 768-dimensional embeddings with good semantic resolution
- Keeps first-time setup lighter than larger embedding models

`qwen3-embedding:0.6b` is a valid future upgrade if retrieval quality becomes more important than setup size.

---

## Consequences

- Users must install Ollama before running the app (covered in setup scripts).
- First-time setup downloads roughly 3 GB of model data (requires internet once).
- After setup, the app is 100% offline.
- The `llm.model` key in `config.yaml` lets users switch models without code changes.
- If a future Apache-2.0 model improves quality or reliability while preserving the offline Ollama workflow, it can be swapped in `config.yaml`.
