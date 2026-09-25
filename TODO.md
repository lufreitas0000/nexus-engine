# Nexus Engine - Sprint 0 TODO List

This list tracks the critical structural debt cleanup required before any feature work (Sprint 1+) begins.

### 1. `research_graph` Promotion
- [ ] Move `packages/arxiv/research_graph` to `packages/research_graph`.
- [ ] Add standard `pyproject.toml` to `packages/research_graph` and register in root UV workspace.
- [ ] Move `schema.py`, `repository.py`, and `uow.py` from `research_graph/infra/` and `research_graph/src/infra/` to `packages/nexus_db`.
- [ ] Move `obsidian.py` to `packages/nexus_workspace`.
- [ ] Move `external_apis.py` to `packages/arxiv/src/infra/`.
- [ ] Delete `chroma_adapter.py`.
- [ ] Delete original `research_graph/infra/` directories.

### 2. `book_studio` Consolidation
- [ ] Refactor `packages/book_studio/src/` into standard `packages/book_studio/src/{domain,services,infra}` + `tests/`.
- [ ] Consolidate duplicated `assembler.py` and `stitcher.py` (from `src/core/` and `src/pipeline/`).
- [ ] Consolidate duplicated `extractor.py` (from `src/pipeline/` and `src/tools/`).
- [ ] Ensure no code remains in `packages/book_studio/src/` root (other than `main.py` if necessary).

### 3. `arxiv` Structural Deduplication
- [ ] Run `git diff --no-index` on `packages/arxiv/document_converter/adapters/` vs `src/infra/`. Merge logic, delete root `adapters/`.
- [ ] Run `git diff --no-index` on `packages/arxiv/document_processor/adapters/` vs `src/infra/`. Merge logic, delete root `adapters/`.
- [ ] Run `git diff --no-index` on `packages/arxiv/ingestion_engine/adapters/` vs `src/infra/`. Merge logic, delete root `adapters/`.
- [ ] Run `git diff --no-index` on `packages/arxiv/orchestrator/` root vs `src/`. Merge logic, delete root duplicates.
- [ ] For all 4 submodules: Merge `test/` into `tests/` and delete `test/`.

### 4. `arxiv` Legacy Archival
- [ ] Delete/Archive `packages/arxiv/api/`.
- [ ] Delete/Archive `packages/arxiv/automation/`.
- [ ] Delete/Archive `packages/arxiv/front/` (Textual TUI).
- [ ] Move `packages/arxiv/common/` to `packages/nexus_application/` or delete if fully unused.

### 5. `app_spatial_compiler` Naming Standardization
- [ ] Rename `packages/convert/app_spatial_compiler/src/application/` to `src/services/`.
- [ ] Rename `packages/convert/app_spatial_compiler/src/infrastructure/` to `src/infra/`.
- [ ] Update internal imports.

### 6. Validation
- [ ] Run `uv sync --all-packages` to ensure workspace integrity.
- [ ] Run `uv run pytest packages/` and achieve 100% pass rate.
