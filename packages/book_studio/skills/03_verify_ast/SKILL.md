---
name: verify_ast
description: Autonomously audits JSON AST chunks for OCR hallucinations and broken math notation.
---

# Skill: Verify AST

## Purpose
Physics texts suffer from broken inline MathJax bounds (e.g., separating an integral from its limit). This skill verifies and automatically patches the syntax of the raw semantic graphs.

## Execution Requirements
- **Agent Role**: `adversarial_verifier` (Powered by LightLLM Qwen or Gemini Flash)
- **Input**: `$NEXUS_WORKSPACE/garden/ast_chunks/<book_name>/chunk_NNN.json`
- **Output**: Verified `$NEXUS_WORKSPACE/garden/ast_chunks/<book_name>/chunk_NNN_verified.json`

## Process
1. Load the chunk AST into memory.
2. Scan for typical errors:
   - Floating punctuation without spaces.
   - Broken LaTeX environments (e.g., a `$` that is never closed).
   - Random character noise typical of Tesseract OCR failures.
3. Perform a lightweight context analysis using an LLM if the layout confidence score is low.
4. Output the verified JSON. If unrecoverable, emit a flag for human review.
