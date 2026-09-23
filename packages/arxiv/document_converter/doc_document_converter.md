# Document Converter Specification

## 1. Domain Modeling

The document converter translates complex scientific source formats (like LaTeX or PDFs) into structured Markdown AST formats.

1. **Format Translation**: It must accept a path to a LaTeX `.tex` file (or gracefully handle a `.pdf` file if conversion is supported, though LaTeX is prioritized).
2. **Mathematical Equations**: It must preserve math equations. Inline math `$x$` and block math `\[ ... \]` or `\begin{equation}...\end{equation}` should be converted into Markdown math formatting (e.g. `$x$` and `$$...$$`) which is standard for most static site generators or note-taking apps.
3. **Sections**: `\section{}`, `\subsection{}`, etc., should be mapped to `#`, `##`, etc.
4. **Figures & Images**: It should extract figure captions. Since a robust image extraction and optimization pipeline might require complex external dependencies (like poppler or specialized LaTeX compilers), a simplified approach in the first phase is to extract the `\includegraphics` paths or figure `\caption`s into Markdown placeholders.

## 1. Domain Modeling

The document converter translates complex scientific source formats (like LaTeX or PDFs) into structured Markdown AST formats.

- `ConvertedDocument`: A domain model tracking the success, error status, and output path of the final Markdown file.

## 2. Adapters

- `LatexToMarkdownConverter`: Takes the main parsed file and translates it to Markdown.
  - Generates a YAML frontmatter header containing paper metadata (Title, Authors, ID).
  - Uses regex to parse basic LaTeX constructs (sections, subsections, formatting).
  - Maps complex math environments (e.g., `\begin{equation}`) to Markdown math blocks `$$...$$`.
  - Maps figure environments to image placeholders while extracting captions.
  - Implements a secondary fallback integrating `spliter` via a subprocess to parse intractable unstructured PDFs to Markdown using Vision Encoders.
