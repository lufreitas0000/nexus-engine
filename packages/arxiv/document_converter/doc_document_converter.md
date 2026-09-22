# Document Converter Specification

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
