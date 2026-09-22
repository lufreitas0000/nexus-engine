# Kindle Artifact Pipeline & Spliter Integration

## Overview
This project provides a pipeline to compile, optimize, and dispatch documents for optimal reading on Kindle devices. Currently, the tool handles basic PDF optimization (via `spliter`), EPUB compilation from Markdown files, and automated delivery to a Send-to-Kindle email address using SMTP.

## The Vision: Integration with `spliter`
To robustly handle intractable, unstructured binary PDFs (like scanned books and raster images), this repository integrates with [spliter](https://github.com/lufreitas0000/spliter) — a microservice-oriented monorepo designed to ingest such PDFs and systematically reduce them into discrete, semantically pure Chapter objects in Markdown.

### Separation of Concerns
By integrating `spliter` as our core extraction engine, we establish a clean separation of responsibilities:
1. **Extraction (The Black Box):** `spliter` will translate the original, unstructured PDF into structured Markdown.
2. **Compilation & Dispatch (This Repo):** Assuming the entry point is a **Markdown file**, this software will convert the Markdown into highly efficient, Kindle-optimized formats based on the user's specific Kindle model, and handle the final dispatch.

## UI Decision & User Experience
To make this open-source tool truly accessible while remaining fully local, we implemented a dedicated **Local Graphical User Interface (GUI)** using Streamlit to provide the best user experience. A GUI enables:
* Intuitive drag-and-drop for input files (PDFs or Markdown).
* Easy dropdown selection of specific Kindle models (Oasis, Paperwhite, Scribe, etc.) to enforce the correct hardware constraints (margins, resolutions).
* Simple forms for securely managing SMTP credentials, Send-to-Kindle email verification, and format preferences.
* Visual progress and a multi-step workflow.

The entire stack will run fully locally to ensure privacy.

## Roadmap

### Phase 1: Markdown-First Architecture
- [x] **Refactor Entry Points:** Shift the pipeline to assume `.md` as the primary intermediate format.
- [x] **Kindle Model Registry:** Implement a robust configuration system storing hardware constraints for different Kindle generations and models.
- [x] **Enhanced Compilation:** Expand the Markdown-to-EPUB engine to utilize the user's formatting preferences and Kindle model constraints.

### Phase 2: `spliter` Integration
- [x] **Pipeline Orchestration:** Integrate `spliter` (Vision Transformers, AST traversal) as an automated preliminary step when a user uploads a PDF.
- [x] **Intermediate Review:** Allow users to optionally inspect or edit the generated Markdown before it is compiled into the final Kindle format.

### Phase 3: GUI Implementation
- [x] **Framework Selection:** Choose a lightweight local GUI framework.
- [x] **Settings Module:** Build the UI for SMTP verification, target email configuration, and default device selection.
- [x] **Execution Dashboard:** Build the main interface to trigger the pipeline, view logs, and track the translation/dispatch progress.

### Phase 4: Packaging and Open Source Polish
- [x] **Local Deployment:** Provide seamless installation methods (e.g., Docker Compose or bundled executables) to handle both the Python pipeline and the heavy ML dependencies required by `spliter`.
- [x] **Documentation:** Expand technical documentation and contribution guidelines.

---

## Local Usage (Docker)

The easiest way to run the Kindle Artifact Pipeline is via Docker Compose:

```bash
# 1. Clone the repository with its submodules
git clone --recurse-submodules https://github.com/your-username/kindle-artifact-pipeline.git
cd kindle-artifact-pipeline

# 2. Configure environment (optional, can also be done via UI)
cp .env.example .env

# 3. Start the application
docker compose up -d --build
```

The application will be accessible at `http://localhost:8501`.

## Local Usage (CLI / Python)

```bash
# Set up environment and install dependencies
pip install -r requirements.txt
# Ensure pandoc is installed on your system!

# Run the UI locally
streamlit run src/ui/app.py
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
