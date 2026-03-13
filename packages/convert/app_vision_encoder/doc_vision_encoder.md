# App Vision Encoder: Semantic Manifold Generation

## Introduction: The Multimodal Tensor Problem

In the upstream `app_structurizer` module, document pages are strictly segregated by their topological entropy. Digitally structured text ($Q=1.0$) is parsed directly from Unicode manifolds. However, when the structurizer encounters a pure image matrix—such as a photograph, a scientific plot, or a complex architectural diagram—it extracts an opaque spatial tensor $T \in \mathbb{R}^{H \times W \times C}$ (Height, Width, Channels).

Traditional Optical Character Recognition (OCR) operates over $T$ to extract discrete character classes. This is insufficient for multimodal artifacts. An OCR engine scanning a topological map will merely output scattered, nonsensical letters found within the map's legend.

The `app_vision_encoder` exists to execute a strictly semantic mapping:
$$f: \mathbb{R}^{H \times W \times C} \to \Sigma^*$$
Where the continuous pixel manifold is translated into a discrete natural language string $\Sigma^*$ that describes the visual semantic meaning of the image. This string is subsequently injected into the Abstract Syntax Tree (AST), replacing the structural `[ALT Text]` node.

## Chapter 1: The Domain Models and State Immutability

The core of our Hexagonal Architecture relies on the categorical concept that Objects are Types (Entities) and Morphisms are Pure Functions. The Domain layer must be mathematically pure; it cannot perform effectful computations such as hardware I/O or GPU memory allocation.

To model our inputs and outputs, we utilize Python's `@dataclass(frozen=True)`.

### 1.1 The `PhysicalImageReference` (Input Type)
```python
@dataclass(frozen=True)
class PhysicalImageReference:
    file_path: Path
    file_size_bytes: int
````

**Pedagogical Note on Memory Allocation:**

A common antipattern in Python is to eagerly load the file buffer into standard RAM upon instantiation (e.g., `self.bytes = file_path.read_bytes()`). For high-resolution tensors, this causes unbounded heap inflation. By storing only the `Path`, `PhysicalImageReference` acts as a deterministic pointer. We strictly defer the C-level memory allocation of the matrix until the exact microsecond the inference adapter requests it.

The `frozen=True` decorator enforces immutability. Once the state is initialized in memory, it becomes a constant. This eliminates side effects and race conditions, mathematically guaranteeing that the tensor reference cannot be altered by concurrent threads.

### 1.2 The `SemanticDescription` (Output Type)

Python

```
@dataclass(frozen=True)
class SemanticDescription:
    content: str
    metadata: dict[str, str]
```

This is the mapped result in the discrete $\Sigma^*$ space, including operational trace data (e.g., the specific Vision-Language Model used).

## Chapter 2: Structural Subtyping and Dependency Inversion

We must transform the `PhysicalImageReference` into a `SemanticDescription`. However, performing this transformation requires **effectful computation**—either mapping gigabytes of weights into VRAM for local inference or opening HTTP sockets for external API calls.

To isolate the Domain from these side effects, we enforce the Dependency Inversion Principle using a Python `Protocol`.

Python

```
class VisionEncoderPort(Protocol):
    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription: ...
```

**Pedagogical Note on `Protocol`:**

Python is dynamically typed. However, the `typing.Protocol` class introduces **structural subtyping** (analogous to type classes in Haskell or interfaces in Go). It evaluates type satisfaction statically at analysis time rather than dynamically at runtime via inheritance hierarchies. Any class that implements a method with the exact signature of `encode_manifold` implicitly satisfies the `VisionEncoderPort`. The Domain logic orchestrates the workflow using this Protocol, completely ignorant of whether the underlying implementation relies on PyTorch or a REST API.

## Chapter 3: The Infrastructure Adapters (Handling Side Effects)

The infrastructure layer encapsulates all effectful operations. We design two distinct adapters to satisfy the `VisionEncoderPort`, providing execution flexibility based on hardware constraints.

### 3.1 The `LocalQuantizedAdapter` (VRAM Topology)

Executing a full-precision Vision-Language Model (VLM), such as LLaVA, requires computing self-attention over image patches:

$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Where the queries $Q$, keys $K$, and values $V$ represent projection matrices of the visual and text tokens. A 7-billion parameter model in 16-bit float (FP16) requires roughly 14GB of VRAM—exceeding standard consumer GPU limits (e.g., RTX 3050 6GB).

To execute this locally, the adapter utilizes **Quantization**. We map the floating-point weights to lower precision discrete levels (e.g., 4-bit integer space), drastically compressing the volumetric requirement of the matrices at a marginal cost to perplexity.

Furthermore, this adapter implements **Lazy Loading**. The Python import and PyTorch CUDA context allocation are trapped within the `encode_manifold` method constraint. The tensor weights are not loaded into the physical hardware until the function is explicitly invoked.

### 3.2 The `ExternalAPIAdapter` (HTTP Socket Delegation)

When local hardware is utterly insufficient, we delegate the matrix multiplications to an external compute cluster (e.g., OpenAI or Anthropic).

This adapter translates the physical image tensor into a Base64 encoded bytestream and initiates a deterministic network request.

**Pedagogical Note on Socket Behavior:**

When the Python interpreter executes an HTTP request, it opens a network socket. This is a blocking I/O operation. The CPU issues the request over the network stack and then idles, waiting for the remote server's response. In a highly concurrent system, this adapter should eventually be mapped to an asynchronous event loop (`asyncio`) to yield CPU control during the blocking wait, allowing the orchestrator to process other `[ALT Text]` nodes simultaneously.














## Chapter 4: The Extraction Boundary and IPC Memory Layout

In high-performance multimodal systems, the transport layer for tensors is a primary bottleneck. We strictly forbid writing intermediate $H \times W \times C$ decoded matrices to non-volatile memory (e.g., NVMe SSDs). Disk I/O introduces unacceptable latency and degrades the lifespan of the storage medium. An uncompressed $1024 \times 1024$ RGB tensor requires approximately $3.1 \text{ MB}$ of memory; constantly serializing and deserializing these matrices to disk is computationally prohibitive.

Instead, the `app_structurizer` dynamically extracts the image into system RAM as a contiguous byte stream (e.g., PNG or JPEG encoded bytes) or a raw NumPy array. The boundary is absolute: the `app_vision_encoder` is a pure functional black box. It possesses zero knowledge of the PDF container format, Cross-Reference (XREF) tables, or pagination. It simply receives an isolated byte array in RAM and returns a discrete UTF-8 semantic string.

## Chapter 5: Topological Image Identification ($Q$-Factor Routing)

To feed the Vision-Language Model, the system must first identify and isolate the physical image tensors from the document. The extraction vector depends entirely on the topological Quality Factor $Q$ computed by the structurizer.

### 5.1 High Quality ($Q \ge 0.95$): Digital Vector Manifolds
In structurally pure PDFs, images exist as discrete, addressable blocks (`/Type /XObject /Subtype /Image`) within the document's internal XREF table. The structurizer traverses these C-level pointers in $O(1)$ time relative to the text stream. The raw byte payload is copied directly from the PDF container into RAM without any rasterization or rendering of the page itself, preserving the original mathematical encoding of the image.

### 5.2 Low Quality ($Q < 0.95$): Rasterized Scans
When a document is a monolithic scanned image, the structural boundaries collapse. The entire page is a single matrix. To identify figures, we rely on the structurizer's layout detection model (typically a Convolutional Neural Network or Vision Transformer).

During the pre-computation phase, this network generates spatial bounding boxes $(x_0, y_0, x_1, y_1)$ coupled with class probabilities. When a bounding box is classified as `Figure` or `Equation`, the structurizer mathematically slices that specific sub-tensor from the primary page matrix. This localized crop is then piped to the `app_vision_encoder` for semantic translation.

## Chapter 6: Processing Cardinality and VRAM Constraints

The `app_vision_encoder` enforces a strict processing cardinality: **Batch Size = 1**.

Vision-Language Models (VLMs) operate via autoregressive transformer architectures. During inference, the model must maintain a Key-Value (KV) cache for every token in the sequence to compute self-attention.
Because high-resolution images are mapped to hundreds or thousands of projection tokens, the memory complexity scales aggressively.

Attempting to process a batch of multiple image tensors simultaneously on standard consumer hardware (e.g., an RTX 3050 with 6GB of VRAM) will instantly exhaust the heap memory, triggering a fatal CUDA Out-Of-Memory (OOM) exception. By strictly enforcing sequential execution (processing one $H \times W \times C$ tensor at a time), we cap the peak VRAM utilization, guaranteeing system stability at the cost of parallel throughput.


## Chapter 7: The Test-Driven Development (TDD) Axiom and Contract Validation

Testing machine learning applications presents a fundamental contradiction: unit tests must be deterministic and execute in milliseconds, whereas neural network inferences are inherently stochastic and computationally massive.

If our continuous integration (CI/CD) pipeline required allocating a 4-bit LLaVA model into VRAM simply to test our domain logic, the test suite would become intractable. To resolve this, our testing strategy strictly relies on **synthetic tensors** and **deterministic test doubles**.

### 7.1 Synthetic Tensor Generation
We must test the `PhysicalImageReference` state validation without bloating our Git repository with binary Large File Storage (LFS) image files. 

During the `pytest` session initialization, we utilize the `PIL` (Pillow) library to mathematically synthesize a minimal continuous manifold—a uniform $\mathbb{R}^{100 \times 100 \times 3}$ RGB matrix—in system RAM. We flush this synthetic tensor to a temporary OS directory. This provides a valid physical pointer for the Domain to evaluate, executing in microseconds and ensuring our repository remains strictly text-based.

### 7.2 The Deterministic Fake (Test Double)
To test the orchestration and integration boundaries, we implement the `FakeVisionEncoderAdapter`. 

This object acts as an exact structural subtype of the `VisionEncoderPort`. However, instead of executing a self-attention forward pass or opening a blocking HTTP socket, it intercepts the `PhysicalImageReference` and instantaneously returns a hardcoded `SemanticDescription`. 

By injecting this Fake into our Application Service during testing, we mathematically prove that the data routing, memory pipelining, and AST injection logic are sound. If the orchestration successfully pipes the data through the Fake, it is guaranteed to pipe the data through the PyTorch or external API adapters in production, provided they strictly adhere to the Protocol.

### 7.3 Isolated Hardware Verification
The actual infrastructure adapters (`LocalQuantizedAdapter` and `ExternalAPIAdapter`) are excluded from the standard unit test suite. They are isolated using `pytest` markers (e.g., `@pytest.mark.gpu` or `@pytest.mark.network`). 

These tests are executed selectively in controlled environments. For the local adapter, we assert that the CUDA context is successfully initialized and that the model's perplexity on a known ground-truth tensor falls within acceptable statistical bounds. For the external adapter, we mock the HTTP response using libraries like `responses` or `httpx-mock` to verify the deterministic parsing of the JSON payload without incurring API billing costs.
