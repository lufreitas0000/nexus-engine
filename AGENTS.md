# Nexus Engine Agentic Guidance

This file provides context for autonomous agents (like Jules) operating within the `nexus-engine` monorepo.

## Workspace Architecture
This repository uses the `uv` package manager with a workspace configuration.
- The root `pyproject.toml` defines the workspace.
- The independent packages live in `packages/`.
- **CRITICAL:** Do NOT attempt to install via `pip` or `poetry`. You must use `uv`.

## Environment Setup Script
To setup the environment and install all dependencies across the workspace, simply run:
```bash
uv sync
```
To run tests across all packages, run:
```bash
uv run pytest
```

## Architectural Rules
1. **The Strict Boundary:** The engine code (`nexus/`) has been decoupled from the data state (`my-workspace/`). Code inside `packages/` must NEVER attempt to read or write files to relative directories like `../data` or `./books`. 
2. **The `NEXUS_WORKSPACE` Environment Variable:** All paths must resolve dynamically via the `NEXUS_WORKSPACE` env var, which points to the absolute path of the data repository.
3. **Pydantic ASTs:** Raw Markdown strings must not be used as an intermediate exchange format between packages. All document nodes must be serialized/deserialized using explicit Pydantic JSON schemas.
