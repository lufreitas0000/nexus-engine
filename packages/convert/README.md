# Semantic PDF Pipeline

## 1. Executive Summary
A microservice-oriented monorepo designed to ingest intractable, unstructured binary PDFs (raster images) and systematically reduce them into discrete, semantically pure Chapter objects.

## 2. Architecture (Directed Acyclic Graph)
The system is decoupled into three independent Python applications, ensuring strict separation of concerns between tensor-based machine learning and deterministic text parsing.

* **`app_structurizer` (Vision-to-Text):** Ingests raw PDF byte streams. Utilizes Vision Transformers (e.g., Meta's Nougat or Marker) to map $H \times W \times C$ pixel matrices into a highly structured Markdown Abstract Syntax Tree (AST), preserving LaTeX equations and spatial hierarchies.
* **`app_slicer` (AST Traversal):** Ingests the intermediate Markdown artifact. Performs a deterministic $O(N)$ traversal of the Markdown headers (e.g., `# Chapter 1`) to split the document into distinct file artifacts.
* **`app_orchestrator`:** The entry point. Manages the I/O piping, memory buffers, and Celery task queues between the structurizer and slicer.

## 3. Engineering Codex
* **Bounded Contexts:** Each `app_*` directory must maintain its own `requirements.in` and test suite. No cross-app imports are permitted outside of the orchestrator.
* **Intermediate Representation:** Markdown is the mandatory data transfer protocol between App 1 and App 2.
EOF
