# Implementation Roadmap: Semantic PDF Splitter Pipeline

This roadmap details the systematic implementation of the Semantic PDF Splitter Pipeline. The primary goal is to efficiently convert unstructured and structured PDFs into organized, semantic Markdown files. By employing a "smart routing" strategy, we prioritize fast, deterministic parsing over expensive Machine Learning (OCR) inference.

## Core Architectural Principles
* **TDD (Test-Driven Development):** All features will be implemented following TDD using synthetic, programmatic PDF generation to ensure deterministic, fast-running test suites.
* **SOLID Principles:** The system will adhere to SOLID principles, relying heavily on Hexagonal Architecture (Ports and Adapters). Core business logic (Domain) remains pure and completely decoupled from external frameworks, libraries, or machine learning models.
* **Modularity:** The software is designed as a suite of decoupled micro-applications (`app_structurizer`, `app_spatial_compiler`, `app_vision_encoder`) with strict boundaries.
* **CLI-First:** The pipeline will feature a robust Command Line Interface (CLI) serving as the primary entry point for both users and downstream automated systems.

---

## Phase 1: Foundational Domain & CLI Scaffold
**Objective:** Establish the core data models, interfaces, and the CLI entry point.

* [ ] **Domain Modeling:** Implement immutable `@dataclass(frozen=True)` models representing the `RawDocument` (input) and `MarkdownAST` (output).
* [ ] **Adapter Protocols:** Define the `VisionExtractor` interface (Protocol) to abstract away the specific text/image extraction implementations.
* [ ] **CLI Development:** Construct the Typer-based CLI application. Implement commands for input parsing, hardware probing, and dependency injection (routing to real or fake adapters based on flags).
* [ ] **Test Double Implementation:** Create a `FakeVisionExtractor` to enable rapid TDD and CI/CD without requiring physical GPUs.

## Phase 2: Smart Routing & Topological Analysis
**Objective:** Implement the logic to determine *how* a PDF should be processed before executing expensive operations.

* [ ] **Heuristic Analysis Engine:** Develop the topological classifier that samples spatial text blocks and calculates Shannon Entropy on the Unicode sequence to definitively identify vector vs. raster documents.
* [ ] **Metadata & Bookmark Parsing:** Integrate efficient open-source C-bindings (e.g., PyMuPDF) to extract existing structural metadata (Tags, Bookmarks, internal XREF dictionaries).
* [ ] **Routing Logic:** Create the Application Service that decides whether a document (or a specific page) can be natively parsed or requires fallback to the OCR engine.

## Phase 3: Spatial Compilation (The Native Path)
**Objective:** Efficiently extract elements from digitally structured PDFs without using ML.

* [ ] **Element Splitting:** Implement deterministic $O(N)$ traversal logic to split the document into tractable sub-elements (text blocks, equations, tables, figures) based on native PDF bounding boxes.
* [ ] **Spatial Markdown Reconstruction:** Route native coordinate data to the `app_spatial_compiler` to reconstruct the Markdown hierarchy (headers, paragraphs, lists) using Euclidean heuristics.
* [ ] **Figure & Table Extraction:** Isolate image tensors and complex structural nodes, preparing them for semantic processing or direct insertion as localized artifacts.

## Phase 4: Vision & OCR Fallback (The ML Path)
**Objective:** Integrate heavy machine learning models for scanned documents and complex visual elements, ensuring they are only invoked when necessary.

* [ ] **Lazy Loading Infrastructure:** Implement the `MarkerVisionAdapter` to execute OCR via models like `marker-pdf`, utilizing lazy-loading to prevent VRAM exhaustion upon application startup.
* [ ] **Vision-Language Model Integration:** Connect the `app_vision_encoder` to process cropped image tensors (figures/diagrams) and return semantic natural language (ALT text).
* [ ] **AST Injection:** Develop the Domain Service (`AstFigureFilter`) to mathematically replace raw image artifacts in the Markdown buffer with their corresponding ALT text or semantic descriptions.

## Phase 5: Concurrency & Orchestration
**Objective:** Ensure the pipeline scales safely within local hardware constraints.

* [ ] **Process Pool Management:** Implement native Python concurrency (`ProcessPoolExecutor`) to batch-process directories of PDFs.
* [ ] **Hardware-Aware Semaphores:** Enforce strict VRAM locks ($N_{workers} = 1$) when utilizing GPU inference, while scaling CPU-bound native parsing tasks across available cores.
* [ ] **Final Pipeline Integration:** Solder the output from `app_structurizer` to the `app_slicer` (AST Traversal) via the Orchestrator, ensuring the final output is a cleanly separated set of Markdown artifacts (e.g., one per chapter).
