# Changelog

All notable project changes should be documented here.

## Unreleased

### Security

- Downgraded `chromadb` from `1.5.9` to `0.6.3` to avoid CVE-2026-45829, a pre-authentication code injection issue reported against ChromaDB Python versions `1.0.0` and later.
- Kept ChromaDB usage in-process via `PersistentClient`; this project must not expose a standalone Chroma server.
- Disabled Chroma anonymized telemetry in the local persistent client configuration.

### Documentation

- Updated setup guidance to recommend Python 3.11 for the current secure ChromaDB pin. On Windows, Python 3.12 may attempt to build `chroma-hnswlib` from source and require Microsoft C++ Build Tools.
