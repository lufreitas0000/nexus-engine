# Domain Specification: App Structurizer

## 1. Theoretical Objective
The `app_structurizer` bounded context is responsible for a singular mathematical transformation: mapping a continuous spatial tensor (an $H \times W \times C$ pixel matrix representing a PDF page) into a discrete, topologically structured Abstract Syntax Tree (AST) encoded as Markdown. 

## 2. Core Domain Models (`src/domain/models.py`)
Our domain state is represented by immutable Data Transfer Objects (DTOs) utilizing standard Python `@dataclass(frozen=True)`. This mimics C-level structs and prevents non-deterministic state mutations during parallel ML processing.

### `RawDocument`
* **Concept:** Represents the input manifold. It acts as a validated pointer to a contiguous byte stream on the physical disk.
* **Attributes:**
  * `file_path (Path)`: Absolute filesystem path.
  * `file_size_bytes (int)`: Memory footprint.
* **Methods:**
  * `__post_init__()`: Validates the physical existence of the binary file at runtime instantiation.
* **Anti-Pattern:** Do **NOT** load the entire byte array into RAM within this class. It is merely a pointer. Defer memory allocation to the specific ML adapter.

### `MarkdownAST`
* **Concept:** The discrete output topology. It contains the successfully parsed Markdown string and extracted metadata.
* **Attributes:**
  * `content (str)`: The raw Markdown string buffer.
  * `metadata (dict[str, str])`: Inference metrics (e.g., confidence scores, processing time).

## 3. Structural Subtyping (`src/domain/ports.py`)
We strictly enforce Dependency Inversion via the `VisionExtractor` protocol.

### `VisionExtractor` (Protocol)
* **Concept:** A Functor that defines the contract for the forward pass of our neural network. 
* **Method:** `extract_ast(self, document: RawDocument) -> MarkdownAST`
* **Design Choice (Why Protocol?):** We use `typing.Protocol` instead of `abc.ABC`. CPython does not need to traverse a deep Method Resolution Order (MRO) tree to check inheritance. It structurally verifies the function signature (Duck Typing). This decouples our pure mathematical logic from heavy C++ machine learning frameworks.
* **Anti-Pattern:** Do **NOT** import `torch`, `marker-pdf`, or any external infrastructure libraries into the `domain/` directory. The domain dictates the interface; the infrastructure (Adapters) must conform to it.

## 4. Usage Heuristics
* **DO:** Inject specific implementations (e.g., `MarkerVisionAdapter`) into your application services at runtime.
* **DO NOT:** Mutate the `RawDocument` or `MarkdownAST` instances. If the AST requires refinement, pipe it through a pure function that returns a *new* `MarkdownAST` instance.
* **DO NOT:** Catch infrastructure-level exceptions (like CUDA Out-Of-Memory errors) inside the domain layer. Let them bubble up to the application orchestrator for retry/reconciliation loops.
