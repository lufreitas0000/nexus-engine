# Project Roadmap: arXiv Scraper

## 1. Proposed Goal

The primary goal of this project is to build an automated system that finds, downloads, and converts scientific papers from arXiv into a clean Markdown format.

Instead of relying solely on keyword metadata searches, the system will integrate with external data sources (like the Semantic Scholar API) to construct a localized, directed citation graph. By computing the topological importance of papers (using Eigenvector Centrality), the system ranks and prioritizes the most impactful research within a specific topic query. Finally, it downloads the source files (LaTeX/PDF), unpacks them, identifies the main document, and converts complex formats into Markdown while preserving math equations and extracting figure captions.

## 2. Current Status

### What has been done:
- **Project Architecture:** The high-level module structure has been established, dividing the system into four main domains: `research_graph` (discovery & ranking), `ingestion_engine` (downloading), `document_processor` (unpacking & file management), and `document_converter` (Markdown translation).
- **Domain Modeling & Specification:** Detailed technical specifications for the `research_graph` have been written (`research_graph/doc_research_graph.md`). This includes domain data structures, graph topology logic, interface contracts (Ports), external API integration strategies (Adapters for arXiv and Semantic Scholar), and database schema design (Infrastructure with PostgreSQL and SQLAlchemy).
- **Environment Setup:** Python dependencies have been defined (`requirements.in` and `requirements.txt`), focusing on asynchronous I/O (`httpx`), robust data validation (`pydantic`), async ORM (`sqlalchemy[asyncio]`), and modern testing frameworks (`pytest`, `pytest-asyncio`).
- **Directory Structure:** The directory scaffolding is in place across the project.

### What needs to be done:
- **Implementation:** The code currently consists mostly of empty `__init__.py` files and documentation. The actual Python code for the domain logic, adapters, and infrastructure needs to be written.
- **Specification for Remaining Modules:** `ingestion_engine`, `document_processor`, and `document_converter` still need detailed technical specifications similar to the `research_graph`.
- **End-to-End Orchestration:** A pipeline or workflow engine needs to be built to connect the four modules seamlessly.
- **Deployment & Infrastructure:** Docker configuration, database initialization scripts, CI/CD pipelines, and production monitoring (logging/metrics) must be set up to make the software deploy-ready.

---

## 3. Development Roadmap to Deploy Readiness

To reach a deploy-ready state, the software development will follow a phased approach:

### Phase 1: Research Graph Foundation (Weeks 1-2)
*Goal: Implement the search, citation graph construction, and paper ranking system.*
- [ ] **Domain & Ports:** Implement `PaperMetadata` dataclass and define `SearchProvider`, `CitationProvider`, and `GraphRepository` protocols.
- [ ] **Graph Logic:** Implement the adjacency matrix and Eigenvector Centrality ranking algorithm.
- [ ] **Adapters:** Build and test the `ArxivAdapter` (XML parsing) and `SemanticScholarAdapter` (JSON parsing) using `httpx`.
- [ ] **Infrastructure:** Implement the PostgreSQL database schema and `UnitOfWork` using SQLAlchemy 2.0 and `asyncpg`.
- [ ] **Testing:** Write unit tests and integration tests using `respx` for mock network calls and Docker-based ephemeral databases.

### Phase 2: Ingestion Engine & Rate Limiting (Week 3)
*Goal: Safely and reliably download source files from arXiv.*
- [ ] **Specification:** Draft `doc_ingestion_engine.md`.
- [ ] **Download Logic:** Implement an asynchronous downloader capable of fetching PDFs and LaTeX source tarballs.
- [ ] **Rate Limiting:** Implement strict rate limiting and backoff/retry mechanisms to comply with arXiv's terms of service and avoid IP bans.
- [ ] **Storage Adapter:** Create a robust local file or object storage adapter to save downloaded raw archives.

### Phase 3: Processing & Conversion Pipeline (Weeks 4-5)
*Goal: Extract raw files and convert LaTeX/PDF to Markdown.*
- [ ] **Specification:** Draft `doc_document_processor.md` and `doc_document_converter.md`.
- [ ] **Document Processor:** Implement archive extraction (zip/tar) and heuristic detection of the "main" LaTeX file (e.g., looking for `\begin{document}`).
- [ ] **Document Converter:** Build the translation engine. Parse LaTeX to extract sections, preserve mathematical formulas natively (MathJax/KaTeX compatible), and extract figure placeholders with their captions.
- [ ] **Image Optimization:** Implement an image compression utility for extracted figures.

### Phase 4: Orchestration & API Layer (Week 6)
*Goal: Tie the modules together into a unified, user-facing application.*
- [ ] **Pipeline Controller:** Write an application service that coordinates the entire flow: `Search -> Graph/Rank -> Download -> Process -> Convert`.
- [ ] **API/CLI:** Develop a REST API (e.g., using FastAPI) or a robust CLI (e.g., using Typer) to allow users to submit topics and retrieve Markdown notes.
- [ ] **Concurrency Management:** Implement task queues (e.g., Celery or native `asyncio` queues) to manage background processing without blocking the API.

### Phase 5: Production Readiness & Deployment (Week 7)
*Goal: Ensure the system is robust, observable, and easy to deploy.*
- [ ] **Containerization:** Write a multi-stage `Dockerfile` for the application and a `docker-compose.yml` to spin up the app alongside PostgreSQL.
- [ ] **Configuration Management:** Centralize environment variables (DB connections, API keys) using `pydantic-settings`.
- [ ] **Observability:** Add structured logging (e.g., `structlog`) and basic metrics for error rates and external API latencies.
- [ ] **CI/CD:** Create GitHub Actions workflows for running `pytest`, `mypy`, `ruff`, and building Docker images on merge.
- [ ] **Documentation:** Finalize user guides and operational runbooks in `README.md`.
