# Agent Operations Guide

This module is designed for AI Agentic Orchestrators (e.g., Claude Code, Antigravity `agy` CLI, or custom orchestration scripts) to autonomously manage the Semantic PDF Pipeline project.

## Autonomous Operation

The orchestration framework is responsible for:
1. **Planning & Task Breakdown:** Analyzing high-level goals and splitting them into granular tasks.
2. **Delegation:** Assigning specific tasks to the appropriate tools or model classes based on complexity.
3. **Execution & Validation:** Running test suites (`make test`), triggering automated workflows, and validating changes (e.g., using `skills/run_tdd_cycle.sh`).

## Model Delegation Strategy

To optimize cost and performance, tasks should be routed based on computational requirements:

*   **Heavy Models (e.g., Gemini Pro, Claude 3.5 Sonnet, GPT-4):**
    *   **Role:** Orchestrator, architecture decisions, complex refactoring, writing complex integration tests, and synthesizing context from multiple modules.
    *   **Usage:** Call these models when a deep understanding of the Hexagonal Architecture and module boundaries is required.
*   **Light Models (e.g., Gemini Flash, Claude 3.5 Haiku, GPT-4o-mini):**
    *   **Role:** Specific implementation tasks, syntax fixing, writing localized unit tests, running bash scripts, or doing targeted file edits.
    *   **Usage:** Delegate tasks to these models using sub-agent bash wrappers or agent CLI tools (e.g., `agy run --model gemini-1.5-flash "fix lint error in spatial.py"`).

## Virtual Cloud Integration (Google Colab)

The repository's ML components, specifically the `vision` module (formerly `app_vision_encoder`), are computationally heavy and require GPU/TPU resources that are typically unavailable locally or in standard CI runners.

*   **Workflow:**
    1. Do not run intensive ML tests locally unless you have guaranteed hardware access.
    2. Package the task or tests using standard python distribution (e.g., wheels) or docker images.
    3. Use the `agent_operations/scripts/trigger_colab_compute.sh` (or equivalent Webhook/API trigger) to dispatch the heavy tasks to a remote Google Colab instance or a cloud VM.
    4. Ensure the remote environment handles the heavy ML model loading and processing, returning the results (Markdown/JSON) back to the orchestrator.

## Resource & Token Efficiency

AI agents operating in this repository must strictly adhere to token usage guidelines:

1.  **Context Management:** Do not dump entire repositories or large files into the context window. Use `grep`, `find`, or the `agent_operations/skills/token_efficiency.py` script to truncate files, extract specific functions, or generate AST summaries.
2.  **Targeted Edits:** Avoid requesting the model to rewrite entire files. Use diff formats, specific line replacements, or targeted AST manipulation.
3.  **Log Piping:** When running test suites, redirect output to a file and parse it. Example: `make test > test_output.log 2>&1 && cat test_output.log | tail -n 50`.

## What NOT To Do (Strict Constraints)

*   **DO NOT** modify the internal logic of the bounding modules (`router`, `spatial`, `vision`) to communicate with each other directly; always use the Orchestrator layer.
*   **DO NOT** run heavy vision extraction processes (VLM inference) directly on the local orchestrator node. Offload this via the Colab/Cloud integrations.
*   **DO NOT** modify the synthetic test data directly (e.g., altering a mock PDF test file to force a test pass). You must fix the code, not the data.
*   **DO NOT** execute commands blindly without reviewing the environment or constraints first.
