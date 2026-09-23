# arxiv_scraper

## Project Goal
This system automates the process of finding, downloading, and converting scientific papers from arXiv into Markdown. It moves beyond simple metadata searching by analyzing how papers cite one another to find the most relevant research on a given topic.

## How it Works
1. **Search & Rank**: You provide a topic. The system finds related papers and uses citation data to rank them by importance.
2. **Download**: The system safely downloads the source files (LaTeX) or PDFs of the top-ranked papers.
3. **Extract**: It opens the downloaded archives and identifies the main document.
4. **Convert**: It converts the source files into a clean Markdown file. It first prioritizes processing the source zip file containing the raw LaTeX (`.tex`) files and images. If the source is unavailable, it falls back to extracting the HTML version or the PDF.
   - **PDF Fallback:** For converting PDFs to Markdown, it integrates [spliter](https://github.com/lufreitas0000/spliter) as a black-box service to process unstructured PDFs into a structured Markdown AST.
   - **Metadata Header:** The final Markdown output will include a YAML frontmatter header containing the paper's metadata.

## Folder Structure Guide

The project is split into four main areas to keep the code organized and easy to maintain:

### /research_graph
This is the search and discovery module.
- It talks to the arXiv and Semantic Scholar APIs.
- It builds a map of which papers cite each other.
- It stores this information in the PostgreSQL database so we don't have to search the same paper twice.

### /ingestion_engine
This is the downloader.
- It manages the connection to the arXiv servers.
- It ensures we download files at a controlled speed so the servers do not block our access.
- It handles retries if a download fails due to a bad connection.

### /document_processor
This is the file manager.
- It takes the downloaded zip or tar files and unpacks them.
- It looks through the files to find which one is the "main" paper (the one that needs to be read).

### /document_converter
This is the translator.
- It takes the scientific paper format and turns it into Markdown, appending a YAML frontmatter header with the paper's metadata.
- It prioritizes raw LaTeX source files, gracefully falling back to HTML or PDF.
- For PDFs, it integrates the external `spliter` tool as a black-box converter.
- It ensures math formulas are preserved and extracts figure captions so that your notes contain the context of the images even if the images themselves are removed.

### /common
Contains shared logic used by all modules, such as settings and basic utility functions.

## Setup
1. **Prepare Environment**: Create a virtual environment and install the requirements.
2. **Start Database**: Use `docker-compose up -d` to start the local database.
3. **Run**: Start a search via the `research_graph` module.

## Roadmap

### What has been done:
- **Project Architecture:** The high-level module structure has been established, dividing the system into four main domains: `research_graph`, `ingestion_engine`, `document_processor`, and `document_converter`.
- **Domain Modeling & Specification:** Detailed technical specifications for the `research_graph` have been written.
- **Environment Setup:** Python dependencies have been defined.
- **Orchestration & API Layer:** A pipeline controller has been built to connect the four modules seamlessly. A REST API (`FastAPI`) has been implemented to allow users to submit topics and retrieve Markdown notes. Task queues have been implemented to manage background processing without blocking the API.
- **Production Readiness & Deployment:** Docker configuration (`Dockerfile` and `docker-compose.yml`) has been set up to make the software deploy-ready alongside PostgreSQL. Application configuration is centralized using `pydantic-settings`. Basic logging (`structlog`) has been added.

### What needs to be done:

### What has been completed:
- **Implementation:** The actual Python code for the domain logic, adapters, and infrastructure has been fleshed out and written across modules.
- **Specification for Remaining Modules:** Technical specifications have been written for `ingestion_engine`, `document_processor`, and `document_converter`.
- **Graph Logic & Data Store Integration:** Implemented the adjacency matrix and Eigenvector Centrality ranking algorithm, storing edge relationships and query results using PostgreSQL.
- **Strict Rate Limiting:** Strict rate limiting and exponential backoff/retry mechanisms have been implemented in the `ingestion_engine` via semaphores and delays to comply with arXiv.
- **Document Processing Pipeline:** Implemented archive extraction (zip/tar), a fallback conversion hierarchy to PDF using `spliter`, simple math formula/figure placeholder preservation, and YAML metadata enrichment on Markdown outputs.
- **CI/CD & Observability:** Implemented CI/CD pipelines using GitHub Actions (`.github/workflows/ci.yml`) alongside structured logging with `structlog`.


### What has been completed:
- **Implementation:** The actual Python code for the domain logic, adapters, and infrastructure has been fleshed out and written across modules.
- **Specification for Remaining Modules:** Technical specifications have been written for `ingestion_engine`, `document_processor`, and `document_converter`.
- **Graph Logic & Data Store Integration:** Implemented the adjacency matrix and Eigenvector Centrality ranking algorithm, storing edge relationships and query results using PostgreSQL.
- **Strict Rate Limiting:** Strict rate limiting and exponential backoff/retry mechanisms have been implemented in the `ingestion_engine` via semaphores and delays to comply with arXiv.
- **Document Processing Pipeline:** Implemented archive extraction (zip/tar), a fallback conversion hierarchy to PDF using `spliter`, simple math formula/figure placeholder preservation, and YAML metadata enrichment on Markdown outputs.
- **CI/CD & Observability:** Implemented CI/CD pipelines using GitHub Actions (`.github/workflows/ci.yml`) alongside structured logging with `structlog`.


### What has been completed:
- **Implementation:** The actual Python code for the domain logic, adapters, and infrastructure has been fleshed out and written across modules.
- **Specification for Remaining Modules:** Technical specifications have been written for `ingestion_engine`, `document_processor`, and `document_converter`.
- **Graph Logic & Data Store Integration:** Implemented the adjacency matrix and Eigenvector Centrality ranking algorithm, storing edge relationships and query results using PostgreSQL.
- **Strict Rate Limiting:** Strict rate limiting and exponential backoff/retry mechanisms have been implemented in the `ingestion_engine` via semaphores and delays to comply with arXiv.
- **Document Processing Pipeline:** Implemented archive extraction (zip/tar), a fallback conversion hierarchy to PDF using `spliter`, simple math formula/figure placeholder preservation, and YAML metadata enrichment on Markdown outputs.
- **CI/CD & Observability:** Implemented CI/CD pipelines using GitHub Actions (`.github/workflows/ci.yml`) alongside structured logging with `structlog`.

For the full detailed roadmap and past phases, see [ROADMAP.md](ROADMAP.md).
