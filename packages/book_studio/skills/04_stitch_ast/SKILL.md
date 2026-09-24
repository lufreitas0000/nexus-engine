---
name: stitch_ast
description: Merges verified JSON chunks back together into a single global Document AST.
---

# Skill: Stitch AST

## Purpose
Because the extraction happens on isolated N-page chunks, paragraphs and equations can be split across boundaries. This orchestrator skill stitches them back together into a continuous book structure.

## Execution Requirements
- **Agent Role**: `book_orchestrator`
- **Input**: Collection of `$NEXUS_WORKSPACE/garden/ast_chunks/<book_name>/chunk_NNN_verified.json`
- **Output**: Single unified `$NEXUS_WORKSPACE/garden/ast/<book_name>.json`

## Process
1. Load all chunk JSONs sequentially.
2. Identify dangling text blocks or equations at the boundary of `chunk_n` and `chunk_n+1`.
3. Concatenate text strings and re-parent logical sections.
4. Extract the Global Table of Contents.
5. Save the final compiled Pydantic `nexus_schema.Document`.
