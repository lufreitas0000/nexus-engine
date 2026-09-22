# Document Processor Specification

## 1. Domain Modeling

The document processor manages the extraction and file structure parsing of the raw compressed archives downloaded from arXiv.

- `ProcessedDocument`: A domain model representing the parsed state of a document, tracking the path to the main file (e.g., `main.tex` or the fallback `.pdf`).

## 2. Adapters

- `ArchiveProcessor`: An adapter that takes a raw file (PDF, tar.gz, or zip).
  - Handles basic PDF passthrough.
  - Extracts compressed files (using Python's `tarfile` and `zipfile` modules).
  - Uses heuristic detection to find the main `.tex` file (e.g., searching for `\begin{document}`).
