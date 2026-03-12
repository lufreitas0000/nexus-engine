
# App Structurizer: A Systems Engineering Monograph

## Introduction: The Physics of Document Parsing

In software engineering, we constantly translate data between continuous and discrete states. A standard text file (`.txt` or `.md`) is discrete; it is a one-dimensional array of UTF-8 tokens. A physical book, or a scanned PDF, is continuous; it is a 2D spatial manifold represented in a computer as an $H \times W \times C$ tensor (Height $\times$ Width $\times$ Color channels) of pixels.

The `app_structurizer` application exists to solve a single mathematical problem: **mapping the continuous spatial tensor of a scanned page into a discrete, topologically structured Abstract Syntax Tree (AST) represented by Markdown.**

To solve this without creating a chaotic, unmaintainable codebase, we employ **Hexagonal Architecture**. This pattern forces us to separate the pure logical "idea" of the application from the dirty realities of reading from a hard drive or managing PyTorch GPU memory.

## Chapter 1: The Domain Models (`src/domain/models.py`)

The Domain is the mathematical core of the application. It knows nothing about databases, web servers, or Machine Learning. It only knows about "States".

We represent these states using Python `@dataclass(frozen=True)`. By making them `frozen`, they become **immutable**. Like a struct in C or a purely functional data type in Haskell, once instantiated, their memory cannot be altered. This eliminates race conditions where two processes try to modify a document simultaneously.

### 1. `RawDocument`

When the application begins, we point it to a file.

```
@dataclass(frozen=True)
class RawDocument:
    file_path: Path
    file_size_bytes: int
```

**The Engineering Choice:** Notice that `RawDocument` does _not_ contain a `bytes` or `bytearray` field. We intentionally do not load the PDF into RAM here. If a user inputs a 2GB textbook, loading it immediately would cause a Heap Exhaustion (Out-Of-Memory) crash. `RawDocument` acts purely as a validated **pointer** to the data residing on the physical disk.

### 2. `MarkdownAST`

This represents the successful output of our transformation.

```
@dataclass(frozen=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]
```

The `content` holds the Markdown text. We call this an AST (Abstract Syntax Tree) because Markdown intrinsically encodes hierarchy (Headers, Lists, Bold text), which our downstream slicing application will mathematically traverse.

## Chapter 2: The Port / Interface (`src/domain/ports.py`)

We know we need to transform a `RawDocument` into a `MarkdownAST`. However, the Domain layer is forbidden from knowing _how_ that happens.

We define a **Protocol** (also known as Structural Subtyping or Duck Typing).

```
class VisionExtractor(Protocol):
    def extract_ast(self, document: RawDocument) -> MarkdownAST: ...
```

**The Engineering Choice:** We use this Protocol to establish a strict boundary. Any code that wants to act as an extractor _must_ accept a `RawDocument` and return a `MarkdownAST`. The Python interpreter checks this signature dynamically. Because the Domain doesn't import PyTorch, we can instantly swap our Machine Learning engine tomorrow (e.g., using GPT-4 Vision instead of Marker) without changing a single line of our core logic.

## Chapter 3: The Application Service (`src/services/extraction.py`)

The Application Service is the conductor of the orchestra. It dictates the workflow but delegates the heavy lifting.

Its primary function is `extract_document_to_markdown`.

**The Logical Flow:**

1. **Instantiate State:** It takes a string file path from the user and wraps it in our safe `RawDocument` pointer.

2. **Dependency Injection:** It calls `extractor.extract_ast(doc)`. The `extractor` was passed into the function as an argument. The Service doesn't know if this extractor is a 5GB PyTorch neural network or a fake mock object used for testing. It just trusts the Protocol.

3. **I/O Boundary:** Once the `MarkdownAST` is returned, the Service flushes the UTF-8 string buffer to the hard drive, writing the final `.md` file.


This function is a mathematically pure orchestration loop.

## Chapter 4: The Infrastructure Adapter (`src/adapters/marker_adapter.py`)

This is where our pure mathematics hits the physical hardware. The `MarkerVisionAdapter` is a concrete implementation of our `VisionExtractor` Protocol.

**The Engineering Choice: Lazy Loading & Hardware Routing**

Machine Learning models (like the Surya layout detector and Texify math OCR used inside `marker-pdf`) are massive arrays of floating-point numbers.

If we put `import marker` at the very top of `marker_adapter.py`, the Python interpreter would immediately allocate gigabytes of memory (RAM/VRAM) the moment the application booted—even if the user only wanted to access a `--help` menu in the CLI!

To prevent this, we use **Lazy Loading**:

```
def _load_models_lazily(self) -> None:
    if self._models is None:
        from marker.models import load_all_models
        self._models = load_all_models()
```

The `load_all_models()` function probes the motherboard. It checks for NVIDIA CUDA drivers (`"cuda"`), Apple Silicon (`"mps"`), or defaults to the `"cpu"`. It maps the tensors directly to the optimal hardware only at the exact millisecond the user requests an extraction.

## Chapter 5: Testing & C-Level Memory (`tests/conftest.py`)

Testing ML systems is notoriously difficult. We cannot run a 10-minute GPU inference every time we run `pytest`, nor can we bloat our GitHub repository with massive PDF binaries.

**The Engineering Choice: Synthetic Data & Fakes**

1. **The Test Double (`FakeVisionExtractor`):** We created a class that satisfies the `VisionExtractor` Protocol but simply returns hardcoded Markdown instantly. This proves our Application Service orchestrates data correctly without requiring a GPU.

2. **C-Level PDF Synthesis:** To test file pointers, we generate a PDF dynamically in RAM using `PyMuPDF` (a C++ binding). We render default Helvetica vectors to a `Pixmap` (pixel array), apply heavy JPEG quantization (lossy compression) to simulate an old, degraded 1970s textbook, and flush it to disk.


Because we do this programmatically, our test suite is entirely deterministic, runs in under a second, and requires zero external binaries.
