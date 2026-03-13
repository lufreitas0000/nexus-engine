
# App Structurizer: A Systems Engineering Monograph

## Introduction: The Physics of Document Parsing

In software engineering, we constantly translate data between continuous and discrete states. A standard text file (like `.txt` or `.md`) is discrete. It is a one-dimensional, highly structured array of characters.

A physical book, or a scanned PDF, is continuous. To a computer, a scanned page is simply a two-dimensional grid of pixels—a matrix of colors. The computer does not inherently know that a specific cluster of black pixels represents the letter "A" or an equation.

The `app_structurizer` application exists to solve this translation problem. Its goal is to take the unreadable pixel grid of a PDF and map it into a structured Markdown document. We choose Markdown because it natively supports text formatting, hierarchical headers (like `# Chapter 1`), and LaTeX mathematics, making it the perfect intermediate representation for downstream processing.

To prevent the code from becoming entangled, we cleanly separate the core logic (the "idea" of the application) from the external tools (like reading files from a hard drive or running machine learning models).

## Chapter 0: The Test-Driven Development (TDD) Axiom

Before writing any application logic, we define its expected behavior through automated tests. In our architecture, testing is not an afterthought; it is the mathematical proof that our logic is sound.

Testing machine learning systems and file parsers is notoriously difficult. If our test suite required loading a 500-page PDF and running a massive neural network on a GPU, running the tests would take minutes or hours.

To solve this, our testing strategy relies on **synthetic data and test doubles (fakes)**. Using the C++ library `PyMuPDF` (imported as `fitz`), we programmatically generate PDFs in RAM during the test phase. We can instantly create a "perfect digital vector" PDF or simulate a "degraded 1970s scanned textbook" by rendering text to an image and applying heavy JPEG compression. Because we synthesize the data programmatically, our test suite is entirely deterministic, runs in milliseconds, and requires no external PDF files to be stored in our repository.

## Chapter 1: The Domain Models

The Domain is the core of the application. It knows nothing about machine learning, neural networks, or databases. It only defines the basic states of our data.

We represent these states using Python `@dataclass(frozen=True)`. By making them `frozen`, they become **immutable**. Once a state is created in the computer's memory, it cannot be altered. This is a crucial pedagogical concept: if data cannot change, we eliminate an entire class of bugs where two different parts of the program try to modify a document at the same time.

### 1. `RawDocument`
When the application begins, we point it to a PDF file on the hard drive.
```python
@dataclass(frozen=True)
class RawDocument:
    file_path: Path
    file_size_bytes: int

```

Notice that we do not load the PDF content into memory here. If a user provides a 2-gigabyte textbook, loading it immediately would crash the program. `RawDocument` acts purely as a validated pointer to the file.

### 2. `MarkdownAST`

This represents the successful output of our transformation.

```python
@dataclass(frozen=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]

```

The `content` holds the final Markdown text.

**Testing the Domain:** We test these models by attempting to instantiate them. For instance, we pass a fake file path to `RawDocument`. The test mathematically proves that the application will immediately raise an error and halt if the physical file does not exist, ensuring we never pass invalid pointers deeper into the system.

## Chapter 2: The Interface Boundaries

We know we need to transform a `RawDocument` into a `MarkdownAST`. However, the Domain layer is forbidden from knowing *how* that machine learning transformation happens.

To enforce this, we define a Protocol (an Interface).

```python
class VisionExtractor(Protocol):
    def extract_ast(self, document: RawDocument) -> MarkdownAST: ...

```

Any code that wants to extract text must accept a `RawDocument` and return a `MarkdownAST`. Because the Domain doesn't import heavy ML libraries like PyTorch, we can instantly swap our Machine Learning engine tomorrow without changing our core logic.

**Testing the Boundaries:**
We test this boundary by creating a `FakeVisionExtractor` in our test suite. This fake object pretends to be a neural network but instantly returns a hardcoded Markdown string. This proves our boundaries work without needing a real GPU.

## Chapter 3: The Application Service

The Application Service is the conductor of the orchestra. It dictates the workflow but delegates the heavy lifting. Its primary function is `extract_document_to_markdown`.

**The Logical Flow:**

1. **Instantiate State:** It wraps the user's file path in a `RawDocument` pointer.
2. **Dependency Injection:** It calls the extractor interface. The Service doesn't know if the extractor is a PyTorch neural network or our fake test object.
3. **I/O Boundary:** Once the text is extracted, the Service writes the final `.md` file to the hard drive.

**Testing the Service:**
We test this orchestration by passing our synthetic PDF and our `FakeVisionExtractor` into the service. We verify that the service correctly pipes the data and successfully writes a `.md` file to a temporary directory.


## Chapter 4: Topology Analysis via Information Theory

Before we subject a PDF to a computationally expensive Vision-Language Model for OCR (Optical Character Recognition), we must deduce its physical memory layout.

Is the document a $H \times W \times C$ raster matrix (a scanned image), or is it a digital vector manifold where the text is explicitly defined by character codes and spatial coordinates?

**The Optimization Goal:**
Eventually, we will utilize vision models to extract complex tables and generate ALT text for figures. However, if the main body text and mathematical equations are already digitally embedded in the PDF, extracting them directly via C-level pointer traversal is orders of magnitude faster. Running a full-page neural network inference on a document that already contains structured text is an unacceptable waste of GPU resources.

Our topology classifier acts as a routing function: if an accessible text manifold exists, we bypass the vision model for the text baseline. If the text is trapped in a raster matrix, we route the page to the ML adapter.

### The Limits of XREF Metadata
A PDF contains an internal dictionary known as the Cross-Reference (XREF) table. We can inspect this metadata in $O(1)$ time. If a document references Font dictionaries (e.g., `/Type /Font`), it implies digital text. If it primarily references Image objects (`/Type /XObject /Subtype /Image`), it implies a scan.

However, metadata is frequently deceptive. Academic PDFs generated by older LaTeX compilers, or documents that have been maliciously obfuscated, often contain digital fonts with broken `ToUnicode` mapping tables. Extracting the text yields a string of garbled characters. To prove the topology is computationally valid, we must analyze the extracted information itself.

### The Unicode Manifold vs. Byte Encoding
When we sample a page using PyMuPDF (`page.get_text()`), the library traverses the spatial blocks and returns a string. In Python, this string is an array of **Unicode code points**, not raw bytes.

It is a critical engineering error to compute the entropy of this data by first encoding it into UTF-8 bytes.

| Method | Utility | Mathematical Flaw |
| :--- | :--- | :--- |
| **UTF-8 Byte Entropy** |  Incorrect | Introduces encoding artifacts. Complex math symbols ($\sum$, $\int$) take 3-4 bytes, artificially inflating entropy with variable-length noise. |
| **ASCII-Only Conversion** |  Lossy | Discarding non-ASCII characters (or replacing them with `?`) destroys the structural topology of the equations. Information is permanently lost. |
| **Unicode Character Entropy** |  Optimal | Captures the true structural information of the sequence. Evaluates the exact symbols the author intended. |

Theoretical limits of these state spaces:

| System / Type | Symbol Count (Alphabet Size) | Theoretical Maximum Entropy |
| :--- | :--- | :--- |
| **ASCII** | 128 | 7.0 bits |
| **Extended ASCII / UTF-8 Bytes** | 256 | 8.0 bits |
| **Empirical PDF Unicode Space** | $\approx 100 - 300$ | $\approx 6.6 - 8.2$ bits |
| **Full Unicode Standard** | $\approx 1.1 \times 10^6$ | $\approx 20.0$ bits |

In an academic paper, the alphabet consists of standard Latin characters, numerals, punctuation, and a distinct subset of mathematical operators. The empirical alphabet size is usually around 150 to 300 unique symbols.

### The Shannon Entropy Heuristic
We model the extracted Unicode string as a discrete stochastic sequence $X$. We compute the zeroth-order Shannon Entropy $H(X)$:

$$H(X) = -\sum_{x \in \Sigma} P(x) \log_2 P(x)$$

Where $\Sigma$ is the empirical alphabet of unique Unicode characters in the string, and $P(x)$ is the empirical probability of character $x$ occurring (the character's frequency divided by the total string length).

Because human language and mathematical syntax adhere to strict grammatical and Zipfian distributions, characters do not appear uniformly. This predictable variance strictly bounds the entropy. For a structurally valid digital document, the Unicode character entropy typically falls within:

$$3.5 \leq H(X) \leq 5.5 \text{ bits/character}$$

If a PDF is a pure scanned image, PyMuPDF extracts nothing, or a highly repetitive string of whitespace. The entropy collapses ($H(X) \to 0$). If the `ToUnicode` map is broken, the extraction yields pseudo-random garbled symbols, driving the distribution toward uniformity and maximizing the entropy ($H(X) > 6.5$).

### The Composite Classification Pipeline
Entropy is scale-invariant. To prevent false positives from degenerate layers (e.g., hidden OCR text consisting only of a few scattered letters), we combine $H(X)$ with absolute geometric limits.

The final mathematical pipeline evaluates:
1.  **Extraction:** Sample a spatial block of text from the manifold.
2.  **Density:** Ensure the absolute character count exceeds a minimum threshold (e.g., length $> 50$).
3.  **Printable Ratio:** Ensure the vast majority of the Unicode code points belong to printable categories, rejecting arrays of control characters.
4.  **Entropy Bound:** Verify $H(X)$ sits within the valid $[3.5, 5.5]$ manifold.

If these constraints are met, we return a Quality Factor $Q = 1.0$, definitively proving the digital vector layout is mathematically sound.

### Testing Topology
Testing this heuristic requires rigorous boundary analysis. In our `pytest` suite, we synthesize two edge-cases in RAM using C-level bindings:

1.  **Pure Raster Test:** We generate a PDF where text is rendered into a JPEG bytestream. We assert that the extraction yields an empty manifold and $Q = 0.0$.
2.  **Structured Vector Test:** We generate a PDF containing native Unicode primitives (including complex characters). We assert that $H(X)$ correctly falls within the natural language bounds, returning $Q = 1.0$.

By testing the mathematical extremes, we prove the stability of the heuristic without maintaining gigabytes of test PDFs.







## Chapter 5: The Infrastructure Adapter (The Machine Learning Engine)

Up to this point, our architecture has been strictly theoretical and mathematically pure. The Domain models define the states, the Application Service orchestrates the workflow, and the Protocol establishes the rules. However, to convert a continuous spatial tensor (the PDF pixels) into a discrete Markdown string, we must eventually execute complex matrix multiplications on a physical processor.

This is the role of the Infrastructure Adapter. It bridges the gap between our pristine, hardware-agnostic Domain and the heavy, C-level reality of PyTorch tensors and computer vision models.

For this specific application, we implement the `MarkerVisionAdapter`, which satisfies the `VisionExtractor` protocol using the `marker-pdf` library.

**The Memory Allocation Problem and Lazy Loading:**
Machine learning models, such as the layout detectors and OCR (Optical Character Recognition) networks used here, consist of massive arrays of floating-point numbers (weights and biases). If we write `import marker` at the very top of our Python script, the Python interpreter will immediately load these gigabytes of weights into the system's physical memory (RAM or VRAM) the moment the application starts.

This is highly inefficient. If a user simply types `--help` in the terminal to read the manual, their computer would freeze for several seconds loading a neural network it never intends to use.

To solve this, we employ a technique called **Lazy Loading**. We encapsulate the heavy import statements inside a function. The neural network is strictly forbidden from entering the physical memory until the exact millisecond the user actually requests a PDF extraction.

**Pseudo-Code Implementation:**
The adapter needs three primary components to fulfill its role successfully:

1. `__init__(self)`: The constructor. It initializes the class but keeps the model memory pointer empty (`None`).
2. `_load_models_lazily(self)`: The memory allocator. It performs the heavy lifting, but only if it hasn't been done already.
3. `extract_ast(self, document)`: The concrete implementation of our Domain Protocol. It receives the `RawDocument`, triggers the lazy load, runs the forward pass of the neural network, and returns the `MarkdownAST`.

```python
class MarkerVisionAdapter:
    def __init__(self) -> None:
        # We start with a null pointer to preserve memory.
        self._models = None

    def _load_models_lazily(self) -> None:
        """
        Allocates the neural network weights into system memory.
        This blocking I/O operation is executed exactly once.
        """
        if self._models is None:
            # The import is trapped inside the function.
            from marker.models import load_all_models

            # Probes the hardware (CUDA/CPU) and maps the tensors.
            self._models = load_all_models()

    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        """
        Executes the tensor transformation from physical PDF to discrete Markdown.
        """
        # 1. Ensure models are in memory
        self._load_models_lazily()

        # 2. Execute the forward pass via the external library
        from marker.convert import convert_single_pdf
        full_text, _, metadata = convert_single_pdf(str(document.file_path), self._models)

        # 3. Map the raw output back into our mathematically pure Domain state
        return MarkdownAST(
            content=full_text,
            metadata={"pages_processed": str(metadata.get("pages", 0))}
        )

```

**Testing the Infrastructure:**
Testing a heavy ML adapter presents a unique challenge. In a continuous integration (CI/CD) pipeline, we often do not have access to a GPU, and running a full OCR model takes too much time for a rapid TDD workflow.

Therefore, our primary test focuses on the *contract*, not the *model parameters*. We create a Test Double known as a Fake (`FakeVisionExtractor`). This Fake implements the exact same `extract_ast` method, but instead of running PyTorch, it immediately returns a hardcoded `MarkdownAST`.

```python
class FakeVisionExtractor:
    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        return MarkdownAST(
            content=f"# Simulated Extraction for {document.file_path.name}",
            metadata={"model": "FakeAdapter_v1"}
        )

```

We test that this Fake perfectly satisfies the `VisionExtractor` protocol. By proving the Fake works, we prove our system's boundaries are sound. The real PyTorch adapter is then tested separately in an isolated environment with actual GPU hardware, validating the matrix outputs against a known ground-truth PDF.

## Chapter 6: The Command Line Interface (CLI) Adapter

The architecture is complete, but it is currently inaccessible. We need an entry point—a mechanism for the user to interact with the system, configure the components, and initiate the extraction. This is the outermost layer of our Hexagonal Architecture: the Command Line Interface (CLI).

**The Goals of the CLI:**

1. **Input Parsing:** Read string arguments from the terminal (e.g., the path to the PDF) and validate them.
2. **Hardware Probing:** Check if the system has a dedicated GPU (CUDA) or if it must rely on the CPU, providing transparency to the user.
3. **Dependency Injection:** This is the most critical step. The CLI decides *which* adapter to use. If the user passes a `--use-fake` flag (essential for our test suite), the CLI instantiates the `FakeVisionExtractor`. Otherwise, it instantiates the heavy `MarkerVisionAdapter`.
4. **Execution:** It passes the inputs and the chosen adapter to the Application Service (`extract_document_to_markdown`).

**Pseudo-Code Implementation:**
We utilize the `typer` library to map Python functions directly to terminal commands.

```python
import typer
from src.services.extraction import extract_document_to_markdown

app = typer.Typer()

@app.command()
def extract(file_path: Path, use_fake: bool = False):
    """
    The main entry point for the user.
    """
    # 1. Input Validation
    if not file_path.exists():
        print("Error: File not found.")
        raise typer.Exit(code=1)

    # 2. Dependency Injection
    # We define the variable by its Protocol, not its concrete class.
    extractor: VisionExtractor

    if use_fake:
        print("Bypassing PyTorch. Using deterministic Fake.")
        extractor = FakeVisionExtractor()
    else:
        print("Loading heavy ML models...")
        extractor = MarkerVisionAdapter()

    # 3. Execution (The Application Service)
    try:
        out_file = extract_document_to_markdown(file_path, extractor, output_dir="./output")
        print(f"Success! Markdown saved to {out_file}")
    except Exception as e:
        print(f"Fatal Error: {e}")
        raise typer.Exit(code=1)

```

By concentrating the Dependency Injection inside the CLI, the rest of the application remains entirely ignorant of the outside world. The Application Service simply receives an object that fulfills the `VisionExtractor` protocol; it does not care if the CLI gave it a PyTorch model or a Test Double.

**Testing the CLI:**
To adhere to our TDD axiom, we must test the terminal commands without actually opening a terminal or waiting for a human to type. We use `CliRunner` from the `typer.testing` module.

The test programmatically invokes the CLI command, passing our synthetic "degraded raster" PDF and the `--use-fake` flag.

```python
def test_cli_extract_with_fake(degraded_raster_book_path: Path, tmp_path: Path):
    # Simulate a user typing in the terminal
    result = runner.invoke(app, [
        "extract",
        str(degraded_raster_book_path),
        "--output-dir", str(tmp_path),
        "--use-fake"
    ])

    # Assert the program did not crash (exit code 0 means success)
    assert result.exit_code == 0

    # Assert the correct console output was displayed
    assert "Using deterministic FakeVisionExtractor" in result.stdout
    assert "Success!" in result.stdout

    # Assert the final file was physically written to the hard drive
    expected_out_file = tmp_path / f"{degraded_raster_book_path.stem}.md"
    assert expected_out_file.exists()

```

This test proves the entire pipeline—from terminal input, to dependency injection, to service orchestration, to I/O flushing—functions perfectly as a unified system, executing in fractions of a second.













## Chapter 7: Topological Refinement (The AST Filter)

The extraction of continuous PDF tensors via `marker-pdf` yields a raw Markdown string. While this string accurately captures the hierarchical text and mathematical equations, it often contains embedded image blocks (either local file references or raw base64 encoded bytestreams).

Our system requirement dictates that figures must be excluded from the final discrete output, replaced entirely by their captions and a structural placeholder (`[ALT Text]`). This placeholder reserves the topological node in the Abstract Syntax Tree (AST) for a future multimodal vision model injection, without polluting the current text buffer.

**The Mathematical Mapping:**
We define this operation as a pure function mapping the AST onto itself: $f: \text{MarkdownAST} \to \text{MarkdownAST}$. Because it modifies the internal state of the document based on deterministic rules, it belongs entirely within the Domain layer.

In Markdown syntax, images are represented as `![Caption](URL)`. We must construct a deterministic parser (utilizing Regular Expressions) that identifies these specific sub-strings, extracts the `Caption` group, drops the `URL` group, and applies the transformation $T$:

$$T(\text{`![Caption](URL)`}) \to \text{`[ALT Text] Caption`}$$

**Pseudo-Code Implementation:**
We implement this as a Domain Service. It does not touch the hard drive or external ML libraries; it simply performs string manipulation in RAM.

```python
import re
from src.domain.models import MarkdownAST

class AstFigureFilter:
    """
    Domain service to mathematically strip raster artifacts from the AST,
    preserving captions and structural nodes.
    """

    # Regex to capture Markdown image syntax: ![caption](url)
    # Group 1 captures the caption.
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\([^)]+\)')

    def filter_ast(self, ast: MarkdownAST) -> MarkdownAST:
        """
        Executes the mapping function over the AST string buffer.
        """
        filtered_content = self.IMAGE_PATTERN.sub(r'[ALT Text] \1', ast.content)

        # We return a newly instantiated immutable object.
        return MarkdownAST(
            content=filtered_content,
            metadata=ast.metadata
        )

```

**Testing the Refinement:**
Because this is a pure function, testing is computationally trivial and execute in microseconds.

We synthesize a `MarkdownAST` containing known edge-cases: standard images, base64 images, and standard links (which must *not* be modified, as they lack the leading `!`). We pass this object to the `AstFigureFilter` and assert that the output string exactly matches our mathematically expected string layout.

```python
def test_ast_figure_filter_strips_images_preserves_captions():
    # Setup the initial state
    raw_content = "Here is a graph: ![Graph 1](data:image/png;base64,...)\nAnd a standard link: [Google](http://google.com)"
    initial_ast = MarkdownAST(content=raw_content, metadata={})

    # Execute the pure mapping function
    filter_service = AstFigureFilter()
    refined_ast = filter_service.filter_ast(initial_ast)

    # Assert the deterministic topological change
    assert "[ALT Text] Graph 1" in refined_ast.content
    assert "data:image/png" not in refined_ast.content
    assert "[Google](http://google.com)" in refined_ast.content # Links remain untouched

```







## Chapter 8: Local Concurrency and the VRAM Bottleneck

To process multiple documents, one might intuitively reach for asynchronous queues (like Celery and Redis). However, for a local application heavily bound by GPU hardware, introducing a distributed message broker is an architectural anti-pattern.

**The Resource Constraint:**
Vision-Language Models require vast matrix allocations in VRAM. If your local hardware (e.g., an RTX 3050) has 6GB of VRAM, a single extraction might consume 4GB. Attempting to run two extractions in parallel will instantly trigger a CUDA Out-Of-Memory (OOM) fatal exception.

Therefore, our processing bottleneck is not Inter-Process Communication (IPC) or network I/O; it is the strict volumetric limit of the GPU memory. Adding Redis simply serializes data across a local network stack, adding latency without increasing floating-point operations per second (FLOPS).

**The Pythonic Solution: Process Pools and Semaphores**
Instead of distributed queues, we utilize Python's native `concurrent.futures.ProcessPoolExecutor` to isolate memory spaces (preventing Python's Global Interpreter Lock from blocking), paired with a strict concurrency limit.

If we are running on a CPU-only machine, we can parallelize across available CPU cores: $N_{workers} = N_{cores} - 1$.
If we are executing on a GPU, we must strictly enforce $N_{workers} = 1$ to maintain a sequential lock on the VRAM, preventing catastrophic heap exhaustion.

**Pseudo-Code Implementation:**
We expand our Application Service to handle batch processing of directories using native libraries.

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import torch

def batch_process_directory(input_dir: Path, output_dir: Path, use_fake: bool):
    pdf_files = list(input_dir.glob("*.pdf"))

    # Calculate mathematically safe concurrency limits
    if use_fake:
        # Fakes require only CPU RAM; we can highly parallelize
        max_workers = 8
    elif torch.cuda.is_available():
        # VRAM is highly constrained; strictly serialize hardware access
        max_workers = 1
    else:
        max_workers = 4 # Standard CPU inference

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Map the extraction function over the array of file pointers
        futures = []
        for pdf in pdf_files:
            futures.append(
                executor.submit(extract_single_document, pdf, output_dir, use_fake)
            )

        for future in futures:
            # Resolving the future catches any exceptions thrown by child processes
            result_path = future.result()
            print(f"Flushed: {result_path}")

```

**Testing Concurrency:**
To test local concurrency, we use our `FakeVisionExtractor`. We programmatically generate an array of 10 synthetic PDFs in a temporary directory. We invoke the batch processor with `max_workers=4`. We then assert that exactly 10 Markdown files were successfully flushed to the output directory, proving that the native IPC and process mapping functions correctly without race conditions.







## Chapter 9: The Multimodal DAG (Routing to Black Boxes)

Our system successfully extracts raw text, classifies memory topologies via Shannon Entropy $H(X)$, and enforces strict local concurrency. However, raw extraction is insufficient for academic and technical domains.

When $Q = 1.0$ (a purely digital document), extracting the text yields a flat sequence of Unicode characters. This process destroys the 2D spatial coordinate data ($\Delta x, \Delta y$) necessary to infer structural formatting. For example, $x^2$ is simply the character `x` followed by `2` with a positive vertical displacement. Furthermore, physical image tensors embedded in the PDF require translation into semantic natural language (ALT text).

Attempting to solve spatial LaTeX compilation, table reconstruction, and semantic Vision-Language modeling within `app_structurizer` violates the Single Responsibility Principle and creates an intractable web of dependencies.

**The Distributed Solution:**
We restrict `app_structurizer` to act exclusively as a **Topological Router and Extractor**. When complex formatting or semantic understanding is required, it delegates the data to highly specialized, isolated modules within our Directed Acyclic Graph (DAG), managed by the `app_orchestrator`.

### 1. The Spatial Compiler Module (`app_spatial_compiler`)
For digitally structured pages, `app_structurizer` extracts the characters and their exact spatial bounding boxes $(x_0, y_0, x_1, y_1)$. This topological graph is passed to `app_spatial_compiler`.

This black-box module ingests the spatial data and applies Euclidean heuristics and lightweight ML layout models to reconstruct the exact Markdown hierarchy. It determines when a block of text is a standard paragraph versus a complex LaTeX equation block, returning strict formatting like:

```latex
$$\int_0^\infty e^{-x^2} dx$$

```

### 2. The Vision Encoder Module (`app_vision_encoder`)

When `app_structurizer` encounters a pure image matrix (`/Type /XObject /Subtype /Image`), it crops the $H \times W \times C$ tensor and passes it to `app_vision_encoder`.

This module acts as the semantic engine. It implements a Vision-Language Model (VLM). Depending on hardware constraints, its internal adapter may load a quantized local model (like LLaVA) or delegate the tensor to an external API. It returns a rigorous semantic description of the graph, photograph, or diagram, which `app_structurizer` then injects into the AST to replace the `[ALT Text]` placeholder.

**Testing the Integration:**
Because `app_structurizer` treats these modules as external black boxes, we test the integration using strict **Contract Testing**.

In our test suite, we mock the responses of the downstream modules. We assert that `app_structurizer` correctly extracts the image tensors and spatial bounding boxes, successfully serializes them into the agreed-upon data transfer format (JSON), and emits them to the inter-process memory buffer without data loss or tensor corruption. We do not test the VLM's accuracy within this module; we strictly test the mathematical routing of the data.
