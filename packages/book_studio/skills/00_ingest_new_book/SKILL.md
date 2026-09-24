---
name: ingest_new_book
description: >
  Complete onboarding guide for ingesting a new academic physics book
  through all pipeline stages (OCR → Verification → LaTeX → Figures).
  Encodes all efficiency lessons learned from the Gordon Baym QM project.
---

# Skill: Ingest a New Book

## Prerequisites

- [ ] The raw PDF is available locally
- [ ] `uv` and `pdflatex` are installed
- [ ] You have a Google Gemini API key (or equivalent) with sufficient quota

---

## Step 0: Create the Book Directory

```bash
BOOK_ID="fazekas_condensed_matter_2003"   # author_topic_year
mkdir -p books/$BOOK_ID/{00_raw,01_segmented,02_stitched,03_verified_md,04_final_tex,05_figures/raw,05_figures/enhanced,06_compiled}
```

Create `books/$BOOK_ID/book.yaml`:
```yaml
book_id: fazekas_condensed_matter_2003
title: "Lecture Notes on Electron Correlation and Magnetism"
author_last: "Fazekas"
author_full: "Patrik Fazekas"
year: 2003
topic: "condensed_matter"
source_pdf: "fazekas_condensed_matter_2003.pdf"
stages:
  ocr_chunk_size: 3        # pages per OCR chunk (memory-safe for WSL)
  ocr_model: flash         # cheapest model for OCR text work
  stage3_model: flash      # markdown verification model
  stage4_model: flash      # LaTeX conversion model (text-to-text, cheap)
  figure_model: pro        # needs vision for figure classification
  parallel_subagents: 3    # max concurrent (avoid quota burst 429)
  quota_threshold: 0.85    # suspend at 85% quota usage
```

Copy the PDF:
```bash
cp /path/to/book.pdf books/$BOOK_ID/00_raw/fazekas_condensed_matter_2003.pdf
```

---

## Step 1: Pre-process (PDF Slicing)

Slice the PDF into chapter-sized chunks to enable token-efficient parallel processing:

```bash
python3 scripts/slice_pdf.py \
  books/$BOOK_ID/00_raw/fazekas_condensed_matter_2003.pdf \
  books/$BOOK_ID/00_raw/chapters/ \
  --chapter-boundaries chapters.txt   # optional: explicit page ranges
```

> **Token Efficiency**: Never send the full PDF to an agent. Each chapter slice should be ≤30 pages. 3-page micro-chunks for OCR; 15-30 page slices for Stage 3 visual verification.

---

## Step 2: Stage 1 — OCR Extraction

```bash
python3 src/main.py run-pipeline \
  books/$BOOK_ID/00_raw/fazekas_condensed_matter_2003.pdf \
  --book-id $BOOK_ID
```

**Key directives for OCR subagent:**
- Chunk size: **3 pages** (prevents WSL OOM kills from Marker OCR)
- The extractor saves chunk state to `01_segmented/{book_id}_chunks/chunk_N.json`
- On restart, already-processed chunks are **skipped** (resumable)
- Images are extracted via `fitz` (PyMuPDF) bounding-box clipping, stored in `05_figures/raw/`

**Common OCR Errors (consult `config/ocr_cognates.json`):**
- `in` → `iℏ` (imaginary unit times ℏ)
- `7r` → `π`
- `l` (ell) → `1` (one) in equations
- `®` → digits in page numbers

> **Overnight shutdown**: The pipeline saves state after every chunk. If interrupted, rerun the same command — it resumes automatically.

---

## Step 3: Stage 3 — Markdown Verification

Spawn `flash` subagents per chapter. Each agent:
1. Reads the segmented Markdown
2. Reads the corresponding **chapter PDF slice** (NOT the full PDF)
3. Fixes OCR errors against the visual source
4. Writes verified files to `03_verified_md/`

**Quota Management:**
- Monitor usage. At **85% quota**, call `dvc commit` and pause.
- Resume after **~4h40m** (Pro quota reset) or **~1h** (Flash quota reset).
- Prefer `flash` for text work; reserve `pro` for complex visual comparison.

**Subagent batch sizes:**
- Use **1 chapter per flash subagent** for chapters >10 chunks
- Use **2-3 chapters per flash subagent** for short chapters (<5 chunks)
- Max **3 parallel subagents** to avoid 429 rate limits

---

## Step 4: Stage 4 — LaTeX Conversion

**Critical insight**: Stage 4 is **text-to-text only**. Do NOT send PDFs to stage 4 agents.

```
Input: books/$BOOK_ID/03_verified_md/
Output: books/$BOOK_ID/04_final_tex/
```

**Directives for Stage 4 subagents:**
- Start each `.tex` with `\section{...}` (no preamble)
- Use modern Dirac bra-ket notation: consult `config/notation.json`
- Use `\hat{}` for all operators
- Use `\mathrm{d}` for differentials
- Batch **3-4 chapters per flash subagent** (pure text, very cheap)

---

## Step 5: Compilation

```bash
python3 books/$BOOK_ID/06_compiled/generate_main_tex.py
pdflatex -interaction=nonstopmode books/$BOOK_ID/06_compiled/${BOOK_ID}.tex
```

Fix any compilation errors before proceeding to figure injection.

---

## Step 6: Figure Enhancement

See `skills/04_figure_enhancement/SKILL.md` for the full agent pipeline.

Quick summary:
1. **Classifier agent** (`pro` model, vision): reads each figure and classifies it
2. **Specialist agents**: TikZ, Python/Matplotlib, or raster cleanup
3. Inject into `.tex` files at `% FIGURE_PLACEHOLDER` markers

---

## Serial vs. Parallel Decision Tree

```
Is the task text-only?
  YES → flash, batch 2-4 chapters, up to 3 parallel
  NO (needs PDF vision) →
    Is the chapter short (<10 pages)?
      YES → flash with sliced PDF, 1-2 chapters per agent
      NO → pro model, 1 chapter per agent, 1 parallel only
```

---

## Quota Safety Protocol

```python
# Pseudocode embedded in orchestrator
if estimated_tokens / quota_limit > 0.85:
    dvc_commit()
    save_pipeline_state()
    sleep(quota_reset_minutes * 60)
    resume_from_saved_state()
```

---

## Naming Convention Reference

| Object | Convention | Example |
|--------|-----------|---------|
| Book ID | `{lastname}_{topic}_{year}` | `baym_quantum_mechanics_1969` |
| Raw PDF | same as book_id | `baym_quantum_mechanics_1969.pdf` |
| Chapter chunks | `{chNN}_{TITLE}.md/.tex` | `03_05_THE_FREE_PARTICLE.tex` |
| Compiled master | `{book_id}.tex/.pdf` | `baym_qm_1969.tex` |
| Figures | `fig_{page}_{block_id}.png` | `fig_042_p_b3.png` |

