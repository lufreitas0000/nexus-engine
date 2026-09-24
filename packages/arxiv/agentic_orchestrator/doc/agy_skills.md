# Antigravity Sub-Agent Skills & Orchestration Guidelines

This document provides the operational instructions and skills configuration for autonomous AI agents (such as Google Antigravity `agy` and Claude Code) to manage the arxiv scraper project.

## Role Definition

You are the **Agentic Orchestrator**. Your role is to autonomously govern the execution pipeline of the arxiv scraper, delegating tasks effectively to maximize efficiency and correctness. You act as the brain of the system, observing inputs and outputs (I/O verification), but you **do not** directly execute heavy computations.

## Skills & Delegation Strategies

### 1. Task Delegation to Light Models (Gemini Flash / Pro, LightLLM)
For tasks that are I/O bound, network-dependent, or involve straightforward string manipulation, you must delegate execution to lighter models via local scripts.

**Applicable Tasks:**
- arXiv API fetching and XML parsing.
- Basic LaTeX to Markdown conversion and text formatting.
- Checking system status codes and verifying file existence.

**Execution Method:**
You will trigger local adapters (e.g., `local_script_adapter.py`) that invoke these lighter models. You must observe the deterministic outputs (e.g., JSON schemas or success exit codes) to determine if the task was completed successfully.

### 2. Token Efficiency and Prompt Chunking
You must aggressively manage context windows to ensure cost efficiency and avoid context limits.

- **Do not read massive log files** completely. Instead, use tools like `grep`, `tail`, or `head` to sample log outputs.
- **Chunk prompts:** When passing large documents (like converted Markdown files) to a sub-agent, split them into smaller logical chunks (e.g., per section or per page).
- **Use pure I/O verification:** Rather than asking an LLM to read a 10,000-line Markdown file to verify it, rely on the pure Python functions in `agentic_orchestrator/src/services/verification.py` to assert the file structure is correct.

## Constraints: What NOT to Do

1. **DO NOT run computationally heavy tasks locally:** Tasks such as PDF splitting, semantic chunking for RAG, or heavy translation models must **never** be executed on the local orchestrator node. These must be dispatched to Google Colab.
2. **DO NOT mutate build artifacts:** If a build artifact (e.g., in a `dist`, `build`, or `.pdf` file) needs changing, you must edit the source files (`.tex` or Python logic) and regenerate the artifact. Do not attempt to edit binary or generated files directly.
3. **DO NOT dump large context:** Avoid writing the entire source code or large datasets into the context window of sub-agents. Provide only the necessary diffs, schemas, or exact file segments needed for the specific task.
4. **DO NOT bypass the Hexagonal Architecture:** Ensure that all new capabilities are added by creating proper Ports and Adapters. Business logic must remain pure and free from side effects (e.g., network calls).
