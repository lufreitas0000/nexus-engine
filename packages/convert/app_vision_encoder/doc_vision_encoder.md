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



