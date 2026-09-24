---
name: slice_pdf
description: Ingests a heavy PDF and slices it into memory-safe page chunks to avoid OOM kills during ML extraction.
---

# Skill: Slice PDF

## Purpose
This skill safely divides massive academic textbooks into digestible N-page chunks (e.g., 3-5 pages). This prevents memory overflow in WSL and limits the context window size required by downstream VLMs.

## Execution Requirements
- **Agent Role**: `ingestion_engineer`
- **Input**: Raw PDF file path (`$NEXUS_WORKSPACE/raw/<book_name>.pdf`)
- **Output**: Chunked PDFs in `$NEXUS_WORKSPACE/raw_chunks/<book_name>/chunk_NNN.pdf`

## Process
1. Validate that the input PDF exists.
2. Read the total page count using `PyMuPDF` (`fitz`).
3. Iterate over the document, copying every 5 pages into a new PDF slice.
4. Save slices sequentially with zero-padded indices (e.g., `chunk_001.pdf`).
5. Generate a manifest `manifest.json` tracking chunk order and original page mappings.
