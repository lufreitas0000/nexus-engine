# Kindle Artifact Pipeline & Spliter Integration

## Overview
This project provides a pipeline to compile, optimize, and dispatch documents for optimal reading on Kindle devices. Currently, the tool handles basic PDF optimization (via `k2pdfopt`), EPUB compilation from Markdown files, and automated delivery to a Send-to-Kindle email address using SMTP.

## The Vision: Integration with `spliter`
To robustly handle intractable, unstructured binary PDFs (like scanned books and raster images), this repository will integrate with [spliter](https://github.com/lufreitas0000/spliter) — a microservice-oriented monorepo designed to ingest such PDFs and systematically reduce them into discrete, semantically pure Chapter objects in Markdown.

### Separation of Concerns
By integrating `spliter` as our core extraction engine, we establish a clean separation of responsibilities:
1. **Extraction (The Black Box):** `spliter` will translate the original, unstructured PDF into structured Markdown.
2. **Compilation & Dispatch (This Repo):** Assuming the entry point is a **Markdown file**, this software will convert the Markdown into highly efficient, Kindle-optimized formats based on the user's specific Kindle model, and handle the final dispatch.

## UI Decision & User Experience
To make this open-source tool truly accessible while remaining fully local, we need a dedicated User Interface.

**Decision: Local Graphical User Interface (GUI)**
While an advanced CLI (e.g., using Textual) is functional for developers, we propose building a **Local Graphical User Interface** (using frameworks like Streamlit, Gradio, Tkinter, or PyQt) to provide the best user experience. A GUI enables:
* Intuitive drag-and-drop for input files (PDFs or Markdown).
* Easy dropdown selection of specific Kindle models (Oasis, Paperwhite, Scribe, etc.) to enforce the correct hardware constraints (margins, resolutions).
* Simple forms for securely managing SMTP credentials, Send-to-Kindle email verification, and format preferences.
* Visual progress bars for the heavy vision-encoding tasks performed by `spliter`.

The entire stack will run fully locally to ensure privacy.

## Roadmap

### Phase 1: Markdown-First Architecture
- [ ] **Refactor Entry Points:** Shift the pipeline to assume `.md` as the primary intermediate format.
- [ ] **Kindle Model Registry:** Implement a robust configuration system storing hardware constraints for different Kindle generations and models.
- [ ] **Enhanced Compilation:** Expand the Markdown-to-EPUB engine to utilize the user's formatting preferences and Kindle model constraints.

### Phase 2: `spliter` Integration
- [ ] **Pipeline Orchestration:** Integrate `spliter` (Vision Transformers, AST traversal) as an automated preliminary step when a user uploads a PDF.
- [ ] **Intermediate Review:** Allow users to optionally inspect or edit the generated Markdown before it is compiled into the final Kindle format.

### Phase 3: GUI Implementation
- [ ] **Framework Selection:** Choose a lightweight local GUI framework.
- [ ] **Settings Module:** Build the UI for SMTP verification, target email configuration, and default device selection.
- [ ] **Execution Dashboard:** Build the main interface to trigger the pipeline, view logs, and track the translation/dispatch progress.

### Phase 4: Packaging and Open Source Polish
- [ ] **Local Deployment:** Provide seamless installation methods (e.g., Docker Compose or bundled executables) to handle both the Python pipeline and the heavy ML dependencies required by `spliter`.
- [ ] **Documentation:** Expand technical documentation and contribution guidelines.

---

## Current CLI Usage (Legacy)
Until the GUI and `spliter` integration are complete, the pipeline operates via a CLI:

```bash
# Set up environment and install dependencies
pip install -r requirements.txt

# Configure SMTP and Send-to-Kindle email
cp .env.example .env
# Edit .env with your credentials

# Run the pipeline
python main.py path/to/document.md
```
