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
# Branch Scope: AST Stitching / Splicing Logic (Phase 4/5 Refinement)

## Branch Name
`feature/ast-stitching`

## Task
Implement the concrete logic that takes a raw Markdown string with image placeholders and a dictionary of extracted ALT texts (from `app_vision_encoder`), and mathematically replaces the placeholders with the actual semantic text.

## Details
This branch is focused on the AST (Abstract Syntax Tree) stitching or splicing logic.
It needs to parse the raw Markdown string that contains image placeholders (e.g., `![image](path)`) and map those placeholders to a dictionary of extracted ALT texts provided by the vision encoder. The result should be a single, cohesive Markdown string where placeholders are replaced with semantic content.

## Why it's safe for parallel work
This is a pure string-manipulation/AST-traversal algorithm that operates strictly on the final output data format, independent of how the PDFs are parsed. It will not conflict with the orchestrator, process pool manager, or the PyMuPDF native tags extraction tasks.
# Branch Scope: feature/concurrency-manager

## Task Description
Build a utility library to manage concurrent execution. Implement `ProcessPoolExecutor` logic that takes a list of PDF file paths and processes them in parallel. Implement the VRAM locking semaphore logic.

## Why it's safe
This is purely infrastructure logic. It can be developed using dummy functions first, then injected into the Orchestrator later.
