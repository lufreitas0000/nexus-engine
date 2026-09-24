---
name: extract_semantics
description: Converts raw PDF chunks into Pydantic AST JSON graphs using the convert microservice.
---

# Skill: Extract Semantics

## Purpose
Transforms continuous pixel and vector layouts from PDF chunks into a discrete, hierarchical `nexus_schema.ExtractionResult` JSON.

## Execution Requirements
- **Agent Role**: `spatial_compiler_agent`
- **Input**: `$NEXUS_WORKSPACE/raw_chunks/<book_name>/chunk_NNN.pdf`
- **Output**: `$NEXUS_WORKSPACE/garden/ast_chunks/<book_name>/chunk_NNN.json`

## Process
1. For each `chunk_NNN.pdf`, invoke the `convert` package.
2. The `convert` engine calculates the topological `q_factor`.
3. **If Vector-based**: Run the mathematical layout mapping via `CompositeSpatialCompiler`.
4. **If Raster-based**: Offload image blocks to the Vision LLM endpoint.
5. Serialize the extracted text, equations, and images into the unified Pydantic JSON AST.
6. Save the `.json` output to the garden.
