# PDF to RAG Markdown Converter

This repository provides an automated pipeline to convert legacy PDF books into digestable markdown chunks optimized for Retrieval-Augmented Generation (RAG) systems.

## Architecture
The system is built on a modular architecture enforcing strict separation of concerns:
- **`app_orchestrator`**: Manages the execution pipeline and inter-module data flow.
- **`app_vision_encoder`**: Handles external multimodal API integrations (Gemini, Local Quantized) for visual block extraction.
- **`app_spatial_compiler`**: Executes spatial tree logic and geometric tessellation for PDF coordinate mapping.
- **`app_structurizer`**: Stitches AST representations and coordinates logical markdown output.

## CI/CD
Testing is strictly enforced on Python >= 3.11.
