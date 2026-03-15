# App Spatial Compiler: Geometric Reconstruction of 1D Syntactic Trees

## Introduction: The Asymmetry of Computational Cost

In the processing of digital documents, we frequently encounter the problem of state regression. Consider a natively digital PDF, such as a recent publication generated directly via `pdflatex`. The document is structurally perfect. The Unicode characters and their precise physical bounding boxes exist deterministically in the file's C-level memory.

If we ignore the topological Quality Factor ($Q$) and route this document to a Vision-Language Model (VLM), we force a state regression. The PDF library renders the discrete vector document into a continuous pixel matrix $\mathbb{R}^{H \times W \times C}$. We intentionally destroy the perfect, discrete structural data to create a continuous image tensor. Subsequently, the VLM executes billions of floating-point operations (FLOPS) in GPU VRAM to "guess" the characters and spatial layouts that were already explicitly defined in the source memory. This operation incurs a massive computational debt.

The `app_spatial_compiler` module exists to exploit the asymmetry of computational cost when $Q \ge 0.95$. Instead of rendering a tensor, we execute Direct Memory Access (DMA) to extract a set of discrete nodes:

$$N = \{ (c_i, x_{0i}, y_{0i}, x_{1i}, y_{1i}) \}$$

Where $c_i \in \Sigma$ is the Unicode character, and the coordinates define its Euclidean bounding box. The module then utilizes deterministic geometric heuristics on the CPU to reconstruct paragraphs and equations. This requires $O(N \log N)$ standard CPU instructions, utilizing effectively zero VRAM and completing in fractions of a millisecond.

## Chapter 1: The Domain Models and Memory Contiguity

The categorical concept that Objects are Types (Entities) and Morphisms are Pure Functions governs our Hexagonal Architecture.

### 1.1 The `SpatialNode` (Input State)
```python
@dataclass(frozen=True, slots=True)
class SpatialNode:
    char: str
    x0: float
    y0: float
    x1: float
    y1: float

```

**Pedagogical Note on Memory Allocation:**
By default, Python objects allocate a dynamic `__dict__` to store attributes, resulting in scattered heap memory pointers. In geometric algorithms requiring $O(N \log N)$ sweeps over thousands of nodes, cache misses become a severe performance bottleneck.

By passing `slots=True` to the dataclass, we suppress the dictionary creation. The Python interpreter allocates a strict, contiguous memory block for the string pointer and the four 64-bit floats. This ensures spatial locality in the CPU cache (L1/L2) during iterative Euclidean distance calculations. The `frozen=True` constraint guarantees mathematical immutability, preventing side effects during concurrent mapping operations.

### 1.2 The `MarkdownAST` (Output State)

```python
@dataclass(frozen=True, slots=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]

```

The discrete topological output of the compiler, containing the 1D string buffer and operational trace data.

## Chapter 2: Structural Subtyping and Dependency Inversion

We define the primary transformation via a Python `Protocol`. This isolates the Domain logic from the specific Application Service orchestrating the data flow.

```python
class SpatialCompilerPort(Protocol):
    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST: ...

```

If deterministic geometric heuristics fail on a complex node cluster (e.g., a highly nested LaTeX commutative diagram), we must delegate that specific bounding box to a fallback adapter (such as a lightweight math-OCR model). We enforce Dependency Inversion here as well:

```python
class EquationFallbackPort(Protocol):
    def resolve_subgraph(self, bounds: tuple[float, float, float, float]) -> str: ...

```

## Chapter 3: Algorithmic Implementation (Pure Morphisms)

The core functionality is encapsulated within the `GeometricParser` domain service. It applies pure functional mappings over the `Sequence[SpatialNode]`.

### 3.1 Baseline Clustering ($O(N \log N)$ Projection)

The algorithm projects the 2D spatial nodes onto the Y-axis. It groups characters $c_i$ into a single line $L_k$ if their vertical baselines $y_{0i}$ are within a strict tolerance $\epsilon_{font}$.

$$L_k = \{ (c_i, \vec{r}_i) \in N \mid |y_{0i} - \mu_{y}(L_k)| < \epsilon_{font} \}$$

**Implementation:** We execute Python's native Timsort: `nodes.sort(key=lambda n: (n.y0, n.x0))`. This guarantees $O(N \log N)$ worst-case time complexity. We then perform an $O(N)$ linear scan, accumulating nodes into a list representing $L_k$ until $y_{0i} - y_{0(i-1)} > \epsilon_{font}$, which triggers a line break.

### 3.2 Block Formation (Paragraphs and Headers)

Once lines $L_k$ are established, we compute the vertical displacement: $\Delta y = y_0(L_{k+1}) - y_1(L_k)$.

* If $\Delta y \approx \text{line\_height}$, we map the arrays into a continuous paragraph block.
* If $\Delta y > \epsilon_{paragraph}$, we inject a double newline `\n\n` into the AST buffer.
* If the bounding box height $(y_1 - y_0)$ of $L_k$ exceeds the document's statistical median by $> 1.5\sigma$, we prepend the Markdown header token (`#`).

### 3.3 Mathematical Formulation (LaTeX Reconstruction)

When mathematical operator codes (e.g., $\int, \sum$) are detected, baseline clustering is suspended. We transition to 2D topological mapping:

* **Superscripts:** If $x_{0j} > x_{1i}$ (node $j$ is right of node $i$) and $y_{1j} < \mu_{y}(L_i)$ (bottom of $j$ is above the baseline of $i$), we map to $c_i \text{\textasciicircum} \{c_j\}$.
* **Fractions:** If an abnormally wide horizontal node (e.g., the minus/fraction line code point) is detected, we compute bounding box intersections to assign nodes to the numerator and denominator arrays, yielding `\frac{num}{den}`.

## Chapter 4: The Test-Driven Development (TDD) Axiom

Testing geometric algorithms with physical PDF files is a severe antipattern. It couples the pure mathematical domain to filesystem I/O and external C++ PDF parsing libraries.

### 4.1 Synthetic Geometric Manifolds

In our `pytest` suite, we construct **synthetic arrays** of `SpatialNode` objects directly in standard RAM.

To test the superscript algorithm, we explicitly instantiate:

```python
nodes = [
    SpatialNode(char="x", x0=10.0, y0=20.0, x1=15.0, y1=25.0),
    SpatialNode(char="2", x0=16.0, y0=15.0, x1=19.0, y1=19.0) # Elevated Y
]

```

We inject this sequence into the `GeometricParser` and mathematically assert that the output string matches `"x^{2}"`. This executes in microseconds and allows us to test infinite topological edge cases (e.g., collision, overlapping bounding boxes) deterministically.

### 4.2 Integration Testing and Test Doubles

To test the Sub-Routing Fallback, we implement a `FakeEquationFallbackAdapter` in `conftest.py`. When the `GeometricParser` calculates a variance threshold failure, it emits the bounding box coordinates to this Fake, which instantly returns a hardcoded LaTeX string (e.g., `\int E \cdot da`). This mathematically proves the conditional routing logic without invoking actual ML tensors.

## Appendix A: Dependency Substrates and Python 3.12 Rigor

This module enforces a strictly minimized dependency graph to maximize pure computational throughput.

* **`itertools` and `math` (Standard Library):** The core algorithms utilize `itertools.groupby` for localized clustering and `math.isclose` for Euclidean tolerance checks. Avoiding external libraries like NumPy for these $O(N)$ 1D array sweeps avoids the C-extension context-switching overhead, which is computationally detrimental for small $N$ lists.
* **`pytest`:** The exclusive testing framework, utilized for its rigorous fixture dependency injection architecture.
* **`collections.abc`:** In accordance with Python 3.12 (PEP 585), we strictly use `collections.abc.Sequence` and `collections.abc.Callable` for type hinting input arrays and behaviors, reserving the `typing` module exclusively for `Protocol`.
