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
