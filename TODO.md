# Nexus Engine - Sprint 0 TODO List

This list tracks the critical structural debt cleanup required before any feature work (Sprint 1+) begins.

### 0.1 Lock Namespace & Promote `research_graph` + Scaffold `nexus_db`
- [ ] Promote `packages/arxiv/research_graph` to `packages/research_graph` with its own `pyproject.toml`.
- [ ] Diff `packages/arxiv/research_graph/{domain,ports,infra,adapters,test}` against `packages/arxiv/research_graph/src/{domain,services,infra}` and `tests/`.
- [ ] Move pure graph domain/services to `packages/research_graph`.
- [ ] Move SQLite `schema.py`, `repository.py`, `uow.py` to `packages/nexus_db`.
- [ ] Move `obsidian.py` to `packages/nexus_workspace`.
- [ ] Delete `chroma_adapter.py`.

### 0.2 Deduplicate `packages/arxiv/**`
- [ ] Archive/delete `packages/arxiv/{api,automation,front}`.
- [ ] Delete root scratch files (`fix_ci.py`, `fix_ci2.py`, `review.txt`, `parallel_plan.txt`, `ROADMAP.md`).
- [ ] Diff and merge root vs `src/` and `test/` vs `tests/` across `document_converter`, `document_processor`, `ingestion_engine`, and `orchestrator`.
- [ ] Consolidate `orchestrator`'s root `queue.py` and `worker.py` into `src/infra/`.
- [ ] Reorganize `agentic_orchestrator/src/` (adapters, ports, infra) into standard `domain/`, `services/`, `infra/`.

### 0.3 Refactor `packages/book_studio/` and `packages/convert/**`
- [ ] Deduplicate `assembler.py`, `stitcher.py`, and `extractor.py` inside `packages/book_studio/book_studio/`.
- [ ] Reorganize `book_studio` into PEP-517 layout: `packages/book_studio/src/book_studio/{domain,services,infra}`.
- [ ] Rename `application/` → `services/` and `infrastructure/` → `infra/` in `packages/convert/app_spatial_compiler/src/`.
- [ ] Delete the duplicate `.agents/` directory from `packages/convert/` (keeping the repo root copy).

### 0.4 Align `nexus-workspace` Layout
- [ ] Scaffold `garden/{papers,books,repos,atomic}`, `raw/{pdfs,tarballs,repos}`, `ledger/`, `exports/kindle/`, and `state/`.
- [ ] Migrate `data/01_raw.dvc` to track `raw/`.
- [ ] Clean up unused root `data/02_*` through `data/07_*` directories.
- [ ] Preserve `books/baym_quantum_mechanics_1969/` and `books/fazekas_electron_correlation_1999/` as intermediate staging directories.

### Validation
- [ ] Ensure all packages strictly follow the `packages/<pkg>/src/<pkg>/{domain,services,infra}` layout.
- [ ] Run `uv sync --all-packages` to ensure workspace integrity.
- [ ] Run `uv run pytest packages/` and achieve 100% pass rate.
