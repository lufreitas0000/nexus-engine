---
name: figure_enhancement
description: >
  Multi-agent pipeline for classifying and reproducing figures from ingested books.
  A classifier agent assigns each figure to a reproduction strategy, then specialist
  subagents produce vector-quality reproductions in TikZ, Python, or SVG.
---

# Skill: Figure Enhancement Pipeline

## Overview

Raw figures extracted from OCR pipelines are raster PNGs — often low-resolution and unscalable. This skill replaces them with publication-quality vector reproductions.

## Step 1: Figure Classification

**Agent**: Figure Classifier (use `pro` model — requires vision)
**Input**: `books/{book_id}/05_figures/raw/*.png`
**Output**: `books/{book_id}/05_figures/figure_manifest.json`

### Classifier Prompt Template

```
You are a scientific figure classifier. For each figure image, determine:
1. figure_type: one of [raster_photo, line_diagram, function_plot_2d, function_plot_3d, matrix_table, energy_diagram, feynman_diagram]
2. reproduction_tool: one of [tikz, python_matplotlib, python_plotly, svg_inkscape, keep_raster]
3. complexity: [low, medium, high]
4. brief_description: one sentence describing the figure content

Output as JSON array. Be conservative — prefer keep_raster for photographs and
complex microscopy images. Use tikz for geometric/schematic diagrams. Use
python_matplotlib for function plots.
```

### Classification Decision Guide

| Figure Type | Recommended Tool |
|-------------|-----------------|
| Geometric diagram, circuit, energy level | `tikz` |
| Function plot (1D, 2D curves) | `python_matplotlib` |
| 3D surface / contour plot | `python_matplotlib` or `python_plotly` |
| Simple flow diagram | `tikz` |
| Feynman diagram | `tikz` (tikz-feynman package) |
| Photograph, SEM, crystal structure | `keep_raster` |
| Complex molecular structure | `keep_raster` |

---

## Step 2: Style Guide (Global Constants)

All reproduced figures MUST conform to these style constants defined in `config/style_guide.yaml`:

```yaml
# Global figure style — all enhanced figures must comply
colors:
  primary:   "#2C3E50"   # Dark blue-grey (main lines)
  secondary: "#E74C3C"   # Red (highlight/accent)
  tertiary:  "#3498DB"   # Blue (secondary curves)
  quaternary: "#27AE60"  # Green (third curve)
  neutral:   "#95A5A6"   # Grey (axes, grid)
  background: "white"

typography:
  font_family: "Computer Modern"   # matches LaTeX body font
  axis_label_size: 12
  tick_label_size: 10
  legend_size: 10
  title_size: 13

lines:
  main_linewidth: 1.5
  secondary_linewidth: 1.0
  axis_linewidth: 0.8
  grid_alpha: 0.3

figure:
  dpi: 300           # for raster export
  width_inches: 3.5  # single-column
  height_inches: 2.8
  tight_layout: true
```

---

## Step 3: TikZ Specialist

**Agent**: TikZ Diagram Agent (use `flash` model)

### TikZ Subagent Prompt Template

```
You are a TikZ expert creating scientific diagrams for a physics textbook.

Figure classification: {classification_json}
Original image path: {image_path}

Create a complete, compilable TikZ figure. Rules:
1. Use \begin{tikzpicture}[scale=1.0] ... \end{tikzpicture}
2. Colors: primary=#2C3E50, secondary=#E74C3C, tertiary=#3498DB
3. Line widths: main=1.5pt, secondary=1.0pt, axes=0.8pt
4. Fonts: use \small for labels, \footnotesize for tick marks
5. Include \caption{} and \label{fig:XX} in surrounding figure environment
6. Must compile with pdflatex + tikz package (no external dependencies)
7. Write the output to: books/{book_id}/05_figures/enhanced/{stem}.tex
```

---

## Step 4: Python/Matplotlib Specialist

**Agent**: Matplotlib Plot Agent (use `flash` model)

### Python Subagent Prompt Template

```
You are a scientific visualization expert creating publication-quality plots.

Figure classification: {classification_json}
Original image path: {image_path}

Create a Python script that reproduces this figure. Rules:
1. Use matplotlib with rcParams matching LaTeX style:
   plt.rcParams.update({
     'font.family': 'serif',
     'font.size': 11,
     'axes.linewidth': 0.8,
     'lines.linewidth': 1.5,
     'figure.dpi': 300,
     'text.usetex': True,  # only if LaTeX is available
   })
2. Export to: books/{book_id}/05_figures/enhanced/{stem}.pdf (vector)
3. Also export a PNG backup at 300 DPI
4. Use the style constants from config/style_guide.yaml
5. Write the script to: scripts/figures/{book_id}/{stem}.py
```

---

## Step 5: Figure Injection into LaTeX

Once enhanced figures are ready, inject `\includegraphics{}` commands:

```python
# In each .tex chunk, replace FIGURE_PLACEHOLDER markers
# or insert after the relevant paragraph using page-number heuristics

# Template:
# \begin{figure}[htbp]
#   \centering
#   \includegraphics[width=0.85\linewidth]{fig_042_p_b3}
#   \caption{Caption text from OCR or manual entry.}
#   \label{fig:baym_ch01_fig1}
# \end{figure}
```

The figure injection script is `scripts/inject_figures.py`.

---

## Quality Checklist

- [ ] Figure is vector or ≥300 DPI raster
- [ ] Colors match `style_guide.yaml` palette
- [ ] Font sizes match textbook body font (≈11pt)
- [ ] Figure has `\caption{}` and `\label{}`
- [ ] Compiles without errors with `pdflatex`
- [ ] Visually matches the original (verify by side-by-side comparison)

