# Branch Scope: Pipeline Orchestrator (Phase 5)

## Overview
This branch (`feature/pipeline-orchestrator`) is dedicated to developing the **Pipeline Orchestrator**.
This acts as the main entry point (e.g., `src/pipeline.py` or a new `app_orchestrator` module) that integrates and coordinates the existing services.

## What It Will Do
*   **Coordinate Execution Flow:** Import and sequentially call the CLI/Services of the `router`, `spatial`, and `vision` modules in the correct order.
*   **Consume Public Interfaces:** Sit above the existing modules and only interact with their defined public interfaces (Ports/CLI) and intermediate outputs (e.g., Markdown AST).
*   **Manage I/O and Buffers:** Coordinate the passing of data (I/O piping, memory buffers) between the different processing stages (structurizer, slicer, etc.).

## What It Will NOT Do
*   **Modify Internal Logic:** It will not change the internal logic or data structures of the `router`, `spatial`, or `vision` modules.
*   **Implement Concurrency (Yet):** It will not be responsible for implementing low-level process pool management or VRAM locking logic (this is handled in a separate branch).
*   **Implement AST Stitching:** It will not implement the concrete logic for mathematically replacing image placeholders with extracted ALT texts (handled in a separate branch).
*   **Extract PDF Metadata:** It will not modify the parsing layers to read PDF bookmarks, TOCs, or embedded tags (handled in a separate branch).
