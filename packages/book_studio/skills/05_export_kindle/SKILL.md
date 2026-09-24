---
name: export_kindle
description: Recompiles the unified AST into EPUB/MOBI formats for e-reader consumption.
---

# Skill: Export to Kindle

## Purpose
Bridges the internal `nexus_schema.Document` representation to external user-facing reading devices.

## Execution Requirements
- **Agent Role**: `deployment_agent`
- **Input**: Unified `$NEXUS_WORKSPACE/garden/ast/<book_name>.json`
- **Output**: `$NEXUS_WORKSPACE/exports/<book_name>.epub`

## Process
1. Load the unified AST.
2. Traverse the DOM, translating specific nexus sections to EPUB HTML constructs.
3. Call `convert_ast_to_epub` from the `kindle` package.
4. Execute `kindlegen` or Calibre bridges (if configured) to generate MOBI/AZW3 files.
5. Notify the user that the book is ready for reading.
