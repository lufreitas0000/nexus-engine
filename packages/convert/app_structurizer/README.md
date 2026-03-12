# Domain Specification: App Structurizer

## 1. Objective
The `app_structurizer` application has one specific job: it takes a raw PDF file (which might just be scanned images of text) and converts it into structured Markdown text.

By using Machine Learning (specifically Vision-Language models like Marker or Nougat), we can "read" the pixels on the page and extract the text, equations, and chapter headings cleanly. Markdown is our chosen output format because it is lightweight, universally understood, and perfectly preserves the hierarchical structure of a book (e.g., `# Chapter 1`, `## Section 1.1`).

## 2. Core Domain Models (`src/domain/models.py`)
We use standard Python `@dataclass(frozen=True)` to define our core data structures. Making them `frozen` means they are immutable—once created, they cannot be changed. This prevents accidental bugs where one part of the program modifies data that another part is currently reading.

### `RawDocument`
* **What it is:** A pointer to the PDF file on your hard drive.
* **Why we built it this way:** It only stores the `file_path` and `file_size_bytes`. It deliberately does **not** load the PDF bytes into memory. Loading a 400-page PDF directly into standard RAM before the ML model is ready for it is a massive memory leak risk.
* **Validation:** It checks if the file actually exists when you create it.

### `MarkdownAST` (Abstract Syntax Tree)
* **What it is:** The final output. It holds the extracted text formatted as Markdown.
* **Data:** Contains the `content` (the actual string of text) and `metadata` (like how long the process took, or confidence scores from the ML model).

## 3. Interfaces / Ports (`src/domain/ports.py`)
To keep our code clean and testable, we separate the "idea" of extracting text from the "actual heavy lifting" using an Interface.

### `VisionExtractor` (Protocol)
* **What it is:** A Python `Protocol` that defines a single method: `extract_ast(document: RawDocument) -> MarkdownAST`.
* **Why we use it:** We do not want to hardcode PyTorch or Marker directly into our main application logic. By defining this Protocol, we can easily swap out the ML engine in the future without breaking our code.
* **Testing Benefit:** This allows us to create a "Fake" extractor for our automated tests that just returns a hardcoded Markdown string instantly, rather than waiting 10 minutes for a real neural network to process a PDF during a unit test.

## 4. Next Steps & Implementation Roadmap
Here is what we will implement next in this module:
1. **Mock/Fake Adapter:** Create `FakeVisionExtractor` in our test suite. This will simulate the ML model so we can build out the rest of the application without needing a GPU.
2. **Real ML Adapter:** Implement `MarkerVisionAdapter` in `src/adapters/`. This will be the actual code that loads the `marker-pdf` library, passes the PDF to the local neural network, and returns the Markdown.
3. **Application Service / Use Case:** Write the orchestration function that receives a file path, creates a `RawDocument`, passes it to the extractor, and saves the resulting `MarkdownAST` to disk.
