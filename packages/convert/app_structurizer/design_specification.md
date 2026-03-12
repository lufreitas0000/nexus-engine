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

```python
@dataclass(frozen=True)
class RawDocument:
    file_path: Path
    file_size_bytes: int

```

**The Engineering Choice:** Notice that `RawDocument` does *not* contain a `bytes` or `bytearray` field. We intentionally do not load the PDF into RAM here. If a user inputs a 2GB textbook, loading it immediately would cause a Heap Exhaustion (Out-Of-Memory) crash. `RawDocument` acts purely as a validated **pointer** to the data residing on the physical disk.

### 2. `MarkdownAST`

This represents the successful output of our transformation.

```python
@dataclass(frozen=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]

```

The `content` holds the Markdown text. We call this an AST (Abstract Syntax Tree) because Markdown intrinsically encodes hierarchy (Headers, Lists, Bold text), which our downstream slicing application will mathematically traverse.

## Chapter 2: The Port / Interface (`src/domain/ports.py`)

We know we need to transform a `RawDocument` into a `MarkdownAST`. However, the Domain layer is forbidden from knowing *how* that happens. We define a **Protocol** (also known as Structural Subtyping or Duck Typing).

```python
class VisionExtractor(Protocol):
    def extract_ast(self, document: RawDocument) -> MarkdownAST: ...

```

**The Engineering Choice:** We use this Protocol to establish a strict boundary. Any code that wants to act as an extractor *must* accept a `RawDocument` and return a `MarkdownAST`. The Python interpreter checks this signature dynamically. Because the Domain doesn't import PyTorch, we can instantly swap our Machine Learning engine tomorrow without changing a single line of our core logic.

## Chapter 3: The Application Service (`src/services/extraction.py`)

The Application Service is the conductor of the orchestra. It dictates the workflow but delegates the heavy lifting. Its primary function is `extract_document_to_markdown`.

**The Logical Flow:**

1. **Instantiate State:** Wraps the file path in a `RawDocument` pointer.
2. **Dependency Injection:** Calls `extractor.extract_ast(doc)`. The Service doesn't know if this extractor is a 5GB PyTorch neural network or a fake mock object. It trusts the Protocol.
3. **I/O Boundary:** Flushes the UTF-8 string buffer to the hard drive.

## Chapter 4: Topology Analysis via Information Theory (`src/domain/services/topology.py`)

Before subjecting a PDF to a heavy Vision-Language Model, we must analyze its physical memory layout. A naive approach involves an $O(N)$ traversal of every page to count vector characters. This scales poorly.

Instead, we treat the extraction of semantic meaning from the document manifold as a discrete stochastic process, evaluated via Information Theory.

Let $X$ be a discrete random variable representing the sequence of UTF-8 characters extracted from the first logical page block. The zeroth-order Shannon Entropy $H(X)$ is defined as:

$$H(X) = -\sum_{x \in \Sigma} P(x) \log_2 P(x)$$

where $P(x)$ is the empirical probability mass function of the character $x$.

**The Entropy Heuristic:**
For a valid, dictionary-bound natural language sequence, the distribution $P(x)$ follows Zipfian constraints, bounded mathematically between:

$$3.5 \leq H_{text}(X) \leq 5.0 \text{ bits/character}$$

If the document is a purely raster-based scanned tensor ($H \times W \times C$), a vector extraction yields degenerate noise or an empty set, resulting in $H(X) \to 0$. If an encrypted stream or raw compressed image matrix is parsed as text, it maximizes entropy, approaching $H(X) \to 8$.

By evaluating $H(X)$ in $O(1)$ time, we calculate a continuous Quality Factor $Q \in [0, 1]$. If $Q = 1.0$, we mathematically prove the existence of an accessible digital vector layout, bypassing the need for computationally expensive visual ML inferencing.

## Chapter 5: The Infrastructure Adapter (`src/adapters/marker_adapter.py`)

This is where our pure mathematics hits the physical hardware. The `MarkerVisionAdapter` is a concrete implementation of our `VisionExtractor` Protocol.

**The Engineering Choice: Lazy Loading & Hardware Routing**
Machine Learning models are massive arrays of floating-point numbers. If we executed `import marker` globally, the interpreter would instantly allocate gigabytes of VRAM. To prevent this, we encapsulate the instantiation:

```python
def _load_models_lazily(self) -> None:
    if self._models is None:
        from marker.models import load_all_models
        self._models = load_all_models()

```

This maps the tensors to the optimal hardware only at the exact millisecond the user requests an extraction.

## Chapter 6: Testing & C-Level Memory (`tests/conftest.py`)

Testing ML systems is notoriously difficult. We cannot run a 10-minute GPU inference every time we run `pytest`.

1. **The Test Double (`FakeVisionExtractor`):** A class that satisfies the Protocol but returns hardcoded Markdown instantly.
2. **C-Level PDF Synthesis:** To test file pointers deterministically, we generate a PDF dynamically in RAM using `PyMuPDF` (a C++ binding). We render vectors, apply heavy JPEG quantization to simulate degraded rasters, and flush it to disk in under a second.
