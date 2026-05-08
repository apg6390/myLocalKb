# Third-Party Licenses

This document lists third-party software, models, and tools used by **myLocalKb**, along with their licenses. This project is released under the Apache License 2.0; all dependencies below are compatible with redistribution under that license.

> **Note on model weights:** myLocalKb does **not** redistribute model weights. Models are downloaded at setup time by the end user via Ollama directly from their respective publishers. This project only redistributes the application code.

---

## Runtime Dependencies (Python)

| Package | Version | License | Source |
|---|---:|---|---|
| fastapi | 0.136.1 | MIT | https://github.com/tiangolo/fastapi |
| uvicorn | 0.46.0 | BSD-3-Clause | https://github.com/encode/uvicorn |
| chromadb | 1.5.9 | Apache 2.0 | https://github.com/chroma-core/chroma |
| pypdf | 6.10.0 | MIT | https://github.com/py-pdf/pypdf |
| python-docx | 1.2.0 | MIT | https://github.com/python-openxml/python-docx |
| python-pptx | 1.0.2 | MIT | https://github.com/scanny/python-pptx |
| httpx | 0.28.1 | BSD-3-Clause | https://github.com/encode/httpx |
| python-multipart | 0.0.27 | Apache 2.0 | https://github.com/Kludex/python-multipart |
| pyyaml | 6.0.3 | MIT | https://github.com/yaml/pyyaml |

---

## Development / Test Dependencies

| Package | Version | License | Source |
|---|---:|---|---|
| pytest | 9.0.3 | MIT | https://github.com/pytest-dev/pytest |
| pytest-asyncio | 1.3.0 | Apache 2.0 | https://github.com/pytest-dev/pytest-asyncio |

---

## Notable Transitive Dependencies

| Package | License | Source |
|---|---|---|
| starlette | BSD-3-Clause | https://github.com/encode/starlette |
| pydantic | MIT | https://github.com/pydantic/pydantic |
| anyio | MIT | https://github.com/agronholm/anyio |
| h11 | MIT | https://github.com/python-hyper/h11 |

---

## System Tools

| Tool | License | Notes |
|---|---|---|
| Ollama | MIT | https://github.com/ollama/ollama - not bundled; installed separately by the user |

---

## AI Models (downloaded at setup time via Ollama - not bundled in this repo)

### qwen3:4b (primary LLM)

- **Publisher:** Alibaba Cloud / Qwen Team
- **License:** Apache License 2.0
- **Model card:** https://huggingface.co/Qwen/Qwen3-4B
- **Summary:** You may use, modify, and distribute this model under Apache 2.0. No restrictions on commercial use.
- **Weights location:** Managed by Ollama on the user's machine (`~/.ollama/models/`). Not included in this repository.

### qwen3:8b (optional higher-quality LLM)

- **Publisher:** Alibaba Cloud / Qwen Team
- **License:** Apache License 2.0
- **Model card:** https://huggingface.co/Qwen/Qwen3-8B
- **Summary:** Higher-quality local chat model under Apache 2.0 for machines with more memory and compute headroom.
- **Weights location:** Managed by Ollama on the user's machine. Not included in this repository.

### mistral:7b-instruct (optional fallback LLM)

- **Publisher:** Mistral AI
- **License:** Apache License 2.0
- **Model card:** https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
- **Summary:** Conservative fallback local chat model under Apache 2.0.
- **Weights location:** Managed by Ollama on the user's machine. Not included in this repository.

### phi3:mini (optional fallback LLM)

- **Publisher:** Microsoft Corporation
- **License:** MIT License
- **Model card:** https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- **Summary:** Permissive MIT license; free for commercial and non-commercial use.
- **Weights location:** Managed by Ollama on the user's machine. Not included in this repository.

### nomic-embed-text (embedding model)

- **Publisher:** Nomic AI
- **License:** Apache License 2.0
- **Model card:** https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
- **Summary:** Apache 2.0; free for commercial and non-commercial use.
- **Weights location:** Managed by Ollama on the user's machine. Not included in this repository.

---

## Legal Notes

1. **Model weights are not redistributed.** myLocalKb only ships application code. End users download model weights directly from Ollama's registry, subject to each model's individual license. No model weights are committed to this repository.
2. **All direct Python dependencies are permissively licensed** (Apache 2.0, MIT, BSD variants). None impose copyleft requirements on this project's source code.
3. **ChromaDB** (Apache 2.0) is used as an in-process library. Its license is compatible with this project's Apache 2.0 license.
4. **Ollama** (MIT) is an external tool installed by the user; it is not bundled or statically linked with this project.
5. This project does not use any AGPL, GPL, LGPL, or SSPL licensed components. If a future contributor adds such a dependency, this file and the project license must be reviewed before merging.

---

*Last updated: 2026-05-08*
