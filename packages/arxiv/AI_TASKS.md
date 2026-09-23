# AI Agent Task Sequencing: LaTeX to Markdown Conversion

This document provides a sequential list of tasks designed for AI coding agents to implement the `document_converter` module. The primary goal is to build an orthogonal, resilient LaTeX-to-Markdown conversion pipeline, completely independent of the currently suspended "PDF spliter" module.

These tasks are designed to be assigned one by one, ensuring a clean, modular architecture.

---

## Task 1: Orthogonal Converter Ports & Domain Models
**Objective:** Define the interfaces and data structures for the conversion module without any format-specific logic.

**Agent Prompt Template:**
> "You are building the core domain for the `document_converter` module. Ignore PDF parsing entirely. Define a `DocumentConverterPort` Protocol in `document_converter/ports/converter.py` that takes a file path and returns a string (Markdown). Define any necessary Pydantic models in `document_converter/domain/models.py` for conversion results (e.g., `ConversionResult` containing markdown content, extracted metadata, and a list of image paths). Ensure these are completely format-agnostic."

---

## Task 2: LaTeX Pre-processor and Macro Registry
**Objective:** Implement the logic to discover and expand custom LaTeX macros before parsing the document tree.

**Agent Prompt Template:**
> "You are implementing the `MacroRegistry` and `LatexPreProcessor` for the `document_converter` module. In `document_converter/adapters/latex_preprocessor.py`, write a class that reads a `.tex` file. It must: 1. Extract the preamble (everything before `\begin{document}`). 2. Use regular expressions or a lightweight parser to find `\newcommand` and `\def` declarations. 3. Provide a method to expand these macros within a given block of LaTeX text. The goal is to normalize the LaTeX string so the downstream AST parser doesn't have to handle custom, undefined commands. Write tests using `pytest` in `document_converter/tests/test_macro_expansion.py`."

---

## Task 3: LaTeX AST Parsing & Node Traversal
**Objective:** Parse the normalized LaTeX text into an Abstract Syntax Tree (AST) to distinguish structure (sections, math, text).

**Agent Prompt Template:**
> "We need to parse LaTeX into an AST for the `document_converter` module. Using a library like `pylatexenc` (add it to requirements if needed), implement `LatexASTParser` in `document_converter/adapters/latex_parser.py`. This class should take a normalized LaTeX string and generate an iterable AST. Implement a Visitor pattern (`LatexNodeVisitor`) that allows us to hook into specific nodes like sections, math blocks (`equation`, `align`, `$`), and environments (`figure`, `theorem`). Ensure this parser is entirely decoupled from how the nodes will be rendered into Markdown."

---

## Task 4: Markdown Renderer & Custom Templates
**Objective:** Map LaTeX AST nodes to Markdown strings using customizable templates.

**Agent Prompt Template:**
> "Implement the `MarkdownRenderer` in `document_converter/adapters/markdown_renderer.py`. This class will use the `LatexNodeVisitor` you built previously.
>
> Key Requirements:
> 1. Standard Mapping: `\section{...}` to `# ...`, `\textbf{...}` to `**...**`.
> 2. Math Preservation: Convert inline and block math environments into `$...$` and `$$...$$` natively.
> 3. Custom Templates: Implement a templating system (using standard Python `str.format` or Jinja2) to handle environments like `\begin{theorem}...\end{theorem}` by mapping them to Markdown blockquotes (e.g., `> **Theorem**: ...`).
> 4. Explicitly translate known packages (like `hyperref`'s `\href{url}{text}` to `[text](url)`).
> Write comprehensive tests in `document_converter/tests/test_markdown_renderer.py`."

---

## Task 5: Orchestrator Adapter Integration
**Objective:** Tie the pre-processor, parser, and renderer together into a class that implements the `DocumentConverterPort`.

**Agent Prompt Template:**
> "Now, integrate the LaTeX pipeline. Create `LatexToMarkdownAdapter` in `document_converter/adapters/latex_adapter.py`. This class must implement the `DocumentConverterPort`. When its `convert(filepath)` method is called, it should:
> 1. Read the file.
> 2. Run the `LatexPreProcessor` to expand macros.
> 3. Parse the result into an AST using `LatexASTParser`.
> 4. Render the AST to a Markdown string using `MarkdownRenderer`.
> Ensure this adapter is robust, catches parsing exceptions, and logs warnings without crashing. Do not include or import any logic related to PDFs or the 'spliter' software."