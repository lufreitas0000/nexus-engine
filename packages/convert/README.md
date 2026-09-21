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
EOF
