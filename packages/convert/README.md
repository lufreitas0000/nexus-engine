# Semantic PDF Pipeline

## 1. Executive Summary
A microservice-oriented monorepo designed to ingest both tractable (structured) and intractable (unstructured/raster) PDFs, and efficiently reduce them into organized, semantically pure Markdown files. The system splits the PDFs into small tractable elements (text, equations, tables, figures) using smart routing, prioritizing deterministic native PDF parsing over expensive OCR fallbacks.

For a detailed phased plan of the implementation, please see the [ROADMAP.md](ROADMAP.md).

## 2. Architecture (Directed Acyclic Graph)
The system is a single unified modular monolith `semantic_pdf_splitter`, containing internal bounded modules that maintain strict separation of concerns between structure routing, spatial extraction, and tensor-based machine learning.

* **`router`:** The topological router and extractor. It analyzes the PDF's internal structure using heuristics (like Shannon Entropy). For digitally structured pages, it extracts native text, equations, and bounding boxes. For raster images, it crops the tensors and delegates them. It serves as the CLI entry point.
* **`spatial`:** Ingests spatial data and text bounding boxes from structured PDFs. Applies Euclidean heuristics to reconstruct exact Markdown hierarchies (headers, paragraphs, math blocks) natively without ML inference.
* **`vision`:** The semantic vision engine. Invoked only when necessary (e.g., for scanned images or embedded figures), it processes image tensors using Vision-Language Models to generate semantic Markdown or ALT text for injection.

## 3. Engineering Codex
* **Bounded Contexts:** Each `app_*` directory must maintain its own `requirements.in` and test suite. No cross-app imports are permitted outside of the orchestrator.
* **Intermediate Representation:** Markdown is the mandatory data transfer protocol between App 1 and App 2.

## 4. AI Agent Workflow
The development of this software is orchestrated using specialized AI agent personas located in the `.agents/` directory:
- **Orchestrator (`.agents/orchestrator.agent.md`)**: Drives the lifecycle and assigns tasks.
- **TDD Engineer (`.agents/tdd_engineer.agent.md`)**: Ensures Test-Driven Development is strictly followed.
- **Adversarial (`.agents/adversarial.agent.md`)**: Focuses on finding vulnerabilities and edge cases.
- **Deployment (`.agents/deployment.agent.md`)**: Manages deployment and infrastructure.

These agents utilize automated scripts located in the `skills/` directory to run tests and validate code (e.g., `skills/run_tdd_cycle.sh` and `skills/adversarial_check.sh`).

## 5. CLI Usage & Integrations
The Semantic PDF Pipeline can be interacted with directly from the Command Line Interface via `cli.py`.

### Basic Usage
To view available commands:
```bash
python cli.py --help
```

To convert a PDF:
```bash
python cli.py convert --help
```

### Programmatic Integration
Other software systems (such as external scrapers or automated delivery pipelines) can easily integrate with this repository by invoking the CLI as a subprocess or importing the components directly, relying on the predictable output structured as Markdown ASTs.
