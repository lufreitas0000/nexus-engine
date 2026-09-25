# Nexus Engine

The core execution engine for the Scientific Knowledge Garden.

Nexus Engine is a multi-package Python monorepo (managed by `uv`) designed to process academic papers (arXiv), physics textbooks (PDF OCR), and numerical software repositories (GitHub) into a unified, locally-hosted knowledge graph.

## Architecture

The engine is built strictly on **Hexagonal Architecture**. Domain packages (e.g. `arxiv`, `book_studio`, `convert`, `github_ingestor`) act as pure transformation pipelines (`RawSource -> CanonicalAST`). 

All operational state and orchestration is decoupled into the `nexus_application` service layer and persisted via the `nexus_db` (SQLite) infrastructure. Content provenance is serialized into immutable Markdown files within the data state repository (`nexus-workspace`).

## Getting Started

1. Set up the environment:
```bash
uv sync --all-packages
```

2. The central entry point is the CLI:
```bash
uv run nexus --help
```

See `ROADMAP.md` for the v1.0 architecture plan, and `TODO.md` for the current sprint tasks.
