# Nexus Engine v1.0 — Multi-Agent Constitution

## 1. Architectural Invariants
- **PEP 517 Namespace Layout**: Every package under `packages/<pkg>/` MUST use `packages/<pkg>/src/<pkg>/{domain,services,infra}` and `packages/<pkg>/tests/{unit,integration,canary}`.
- **Categorical Purity**:
  - `domain/`: Pure immutable types (`frozen=True`) and pure mathematical/structural functions. ZERO I/O imports (`os`, `sys`, `subprocess`, `sqlite3`, `aiosqlite`, `httpx`, `requests`, `shutil`, `pathlib.Path.write_text`).
  - `services/`: Pure application/domain orchestration operating strictly over `domain` types and `Protocol` ports.
  - `infra/`: Concrete adapters (SQLite, filesystem, subprocess `latexpand`, HTTP APIs, Ollama/LiteLLM, Gemini).
- **Truth Partition**:
  - `$NEXUS_WORKSPACE/garden/*.md`: Immutable content and provenance YAML only.
  - `$NEXUS_WORKSPACE/ledger/*.jsonl`: Append-only audit logs (`catalog.jsonl`, `citations.jsonl`, `status.jsonl`).
  - `$NEXUS_WORKSPACE/nexus.db`: Derived, rebuildable SQLite + FTS5 index.

## 2. Compute Tier & Credit Conservation Matrix
| Tier | Model | Permitted Tasks |
|------|-------|-----------------|
| **Tier 1 (Local)** | Ollama / LiteLLM `qwen2.5-coder:3b` / `7b` | Import rewrites, `pyproject.toml` scaffolding, docstrings, simple test boilerplate |
| **Tier 2 (Flash)** | `gemini-2.5-flash` | Standard TDD cycles, file diffing, SQLite/CLI wiring, test runner analysis |
| **Tier 3 (Pro)** | `gemini-2.5-pro` / Claude Opus/Sonnet | Complex AST/math algorithms, port design, and Gate 4 Adversarial Reviews |

## 3. Agent Topology & Gate Order
Every task in `TODO.md` must pass sequentially through:
1. **Orchestrator (`.agents/orchestrator.agent.md`)**: Scopes the single task, selects the lowest viable model tier, and prevents scope creep.
2. **TDD Engineer (`.agents/tdd_engineer.agent.md`)**: Writes failing tests first, reconciles duplicate files via `git diff --no-index`, and implements pure morphisms/adapters.
3. **Architecture & Static Validator (`.agents/validator.agent.md`)**: Executes `./skills/validate_architecture.sh` and `./skills/run_tdd_cycle.sh`.
4. **Canary Tester (`.agents/canary_tester.agent.md`)**: Executes `./skills/run_canary_tests.sh` using real unmocked micro-inputs.
5. **Adversarial Auditor (`.agents/adversarial.agent.md`)**: Executes `./skills/adversarial_check.sh` and attempts to falsify the implementation before commit.
