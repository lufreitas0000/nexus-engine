# LaTeX to Markdown Conversion Specification

This document details the architecture and technical requirements for the LaTeX-to-Markdown translation engine within the `document_converter` module. This module is designed orthogonally, ensuring it can operate independently of other format handlers (like HTML or the currently sleeping PDF spliter).

## 1. Goal

To parse `.tex` (LaTeX) source files and transform them into structurally sound Markdown (`.md`) files, preserving mathematical formulas, section hierarchies, and figure placements, while intelligently translating custom macros and LaTeX packages using customizable templates.

## 2. Orthogonal Design Principles

- **Independence**: The LaTeX converter must not rely on PDF extraction logic or HTML parsing logic. It operates purely on the `.tex` syntax tree and related assets (like local images or `.bib` files if necessary).
- **Extensibility**: Custom LaTeX macros (e.g., `\newcommand{\myvec}[1]{\mathbf{#1}}`) must be parsed and substituted before or during the conversion step.
- **Pluggability**: The converter implements a standardized `DocumentConverterPort`. The orchestrator just calls `.convert(path)` without knowing *how* it's implemented.

## 3. Architecture & Flow

### Phase A: Pre-processing & Macro Expansion
1. **Source Discovery**: Identify the entry-point `.tex` file (often containing `\begin{document}`).
2. **Macro Discovery**: Scan the preamble (before `\begin{document}`) and any included `.sty` or `.tex` files for `\newcommand`, `\renewcommand`, `\def`, etc.
3. **Macro Substitution**: Apply these custom definitions across the body of the document to normalize the LaTeX string.

### Phase B: AST Parsing (Abstract Syntax Tree)
1. **Tokenization**: Parse the normalized LaTeX text into an AST using a robust parser (e.g., `pylatexenc` or a custom parser based on `Lark`).
2. **Node Traversal**: Walk the AST to identify blocks (environments, sections, paragraphs, math).

### Phase C: Markdown Rendering & Custom Templates
1. **Mapping Rules**:
   - `\section{...}` -> `# ...`
   - `\textbf{...}` -> `**...**`
   - `\begin{equation}...\end{equation}` -> `$$...$$`
2. **Custom Templates**: For specific LaTeX environments (e.g., `\begin{theorem}...\end{theorem}`) or complex custom macros that don't directly map to Markdown, use custom string templates (e.g., Jinja2 or simple Python format strings) to define how they should appear in the Markdown output. Examples:
   - *Theorem Template*: `> **Theorem {number}**: {content}`
3. **Figure Handling**: Convert `\includegraphics{path/to/img}` to Markdown image syntax: `![Caption](path/to/img)`. If a caption is present in the `figure` environment, use it.

## 4. Subcomponents

- `latex_parser.py`: Handles file reading, preamble extraction, and macro substitution.
- `latex_ast_visitor.py`: Walks the LaTeX structure and dispatches rendering to specific handlers.
- `markdown_renderer.py`: Applies custom templates and generates the final Markdown string.
- `macro_registry.py`: Maintains a dictionary/mapping of discovered macros and their translation rules.

## 5. Implementation Notes

- We need to define standard "Markdown compatible language" mapping for common packages (like `amsmath`, `graphicx`, `hyperref`).
- Ensure all math blocks (`$`, `$$`, `\[`, `\]`, `equation`, `align`) are preserved accurately, as they are a primary feature of arXiv papers.
