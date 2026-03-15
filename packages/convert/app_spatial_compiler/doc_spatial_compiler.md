# App Spatial Compiler: Geometric Reconstruction of 1D Syntactic Trees

## Introduction: The Asymmetry of Computational Cost

In the processing of digital documents, we frequently encounter the problem of state regression. Consider a natively digital PDF generated directly via `pdflatex`. The document is structurally perfect. The Unicode characters and their precise physical bounding boxes exist deterministically in the file's C-level memory.

Transforming this document into a continuous pixel matrix $\mathbb{R}^{H \times W \times C}$ to be processed by a Vision-Language Model (VLM) is a state regression. We intentionally destroy discrete structural data to create a continuous image tensor, forcing the VLM to execute billions of floating-point operations (FLOPS) to approximate data that was already explicitly defined.

The `app_spatial_compiler` module exploits the asymmetry of computational cost when the structural Quality Factor is high ($Q \ge 0.95$). We assume a preprocessing pipeline has executed Direct Memory Access (DMA) to extract a sequence of discrete nodes. We apply deterministic geometric heuristics and topological sorting on the CPU to reconstruct the 1D syntactic tree, requiring $O(N \log N)$ operations and minimal memory footprint.

## Chapter 1: Architectural Invariants and Memory Boundaries

The system strictly adheres to Hexagonal Architecture, isolating pure mathematical transformations from effectful computations and I/O.

### 1.1 Structural Segregation

The bounded context is partitioned into three discrete layers:
1. **`src/domain/`**: The axiomatic core. Contains memory-contiguous Entity definitions (`SpatialNode`), pure structural subtyping (`Ports`), and deterministic geometric functions (Recursive XY-Cuts, KD-Trees). Operates exclusively on mathematical manifolds in RAM.
2. **`src/application/`**: Orchestration logic. Implements Use Cases that bind the Domain to external inputs and dictate the pipeline execution flow.
3. **`src/infrastructure/`**: The effectful boundary. Contains Adapters that fulfill Domain Ports, bridging external systems (e.g., C-level bindings for spatial indexes, VLM network calls for figure parsing).

### 1.2 Domain Models and Memory Contiguity

In our category-theoretic architecture, Objects are Types (Entities) and Morphisms are Pure Functions. The fundamental input Entity is the `SpatialNode`.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SpatialNode:
    char: str
    x0: float
    y0: float
    x1: float
    y1: float

```

Suppressing the dynamic dictionary via `slots=True` ensures the Python interpreter allocates a strict, contiguous memory block. This guarantees spatial locality in the CPU cache during the $O(N \log N)$ Euclidean distance mappings. `frozen=True` ensures mathematical immutability.

The compiler's terminal state is the `MarkdownAST`:

```python
@dataclass(frozen=True, slots=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]

```

## Chapter 2: Structural Subtyping and Dependency Inversion

We define the primary transformations via Python `Protocols` to isolate Domain logic from Infrastructure side effects.

```python
from collections.abc import Sequence
from typing import Protocol
from .models import SpatialNode, MarkdownAST

class SpatialCompilerPort(Protocol):
    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST: ...

class EquationFallbackPort(Protocol):
    def resolve_subgraph(self, bounds: tuple[float, float, float, float]) -> str: ...

```

When deterministic graph grammars cannot parse a localized non-textual region, the infrastructure is invoked via the `EquationFallbackPort` to evaluate the local bounding manifold, preserving the pure function signature of the primary compiler.

## Chapter 3: Algorithmic Implementation (Pure Morphisms)

The algorithms within `src/domain/geometry/` assume the source layout follows strict typographic rules that we exploit topologically.

### 3.1 Global Topological Partial Ordering (Recursive XY-Cut)

Naive $y$-axis sorting is topologically insufficient for mapping non-linear reading orders (e.g., two-column academic layouts) into a 1D AST. The 2D Euclidean space must be partitioned into orthogonal sub-manifolds via a Recursive XY-Cut.

Let the document page be a subspace $S \subset \mathbb{R}^2$. The set of parsed Unicode nodes is $B = \{b_1, \dots, b_n\}$. We define orthogonal projection profiles $P_x(x)$ and $P_y(y)$ to map the density of bounding box spatial intersections along the respective axes.

A valid cut $C$ is an interval where the projection profile evaluates to zero for a continuous distance exceeding a dynamic font-relative threshold $\Delta$:

$$C_y = \{ y \in [y_{min}, y_{max}] \mid P_y(y) = 0 \text{ for distance } > \Delta_y \}$$

$$C_x = \{ x \in [x_{min}, x_{max}] \mid P_x(x) = 0 \text{ for distance } > \Delta_x \}$$

**Execution:**

1. **$y$-axis Partitioning:** Evaluate $C_y$ to separate horizontally distinct blocks (headers, body text, equations).
2. **$x$-axis Partitioning:** For each resulting block, evaluate $C_x$ to isolate independent column structures.
3. **Recursion:** Alternate evaluations until $S$ can no longer be partitioned.

This recursive bisection yields an ordered $N$-ary spatial tree. A depth-first traversal of this tree produces the mathematically correct 1D topological reading order for the macroscopic document blocks.

### 3.2 Spatial Graph Grammars (Equations)

Local mathematical heuristics (e.g., simple bounding box intersection) fail on non-linear, deeply nested tensors (e.g., $R_{\mu \nu} - \frac{1}{2}R g_{\mu \nu} = \kappa T_{\mu \nu}$).

To parse mathematical blocks, the isolated nodes are mapped into a Spatial KD-Tree. This data structure partitions the local $\mathbb{R}^2$ space, enabling $O(\log N)$ spatial queries.

1. **Adjacency Graph:** For each node $v \in V$, we query the KD-Tree for its $k$-nearest neighbors. We construct a directed spatial graph $G = (V, E)$ where edges represent geometric relationships (e.g., `is_subscript_of`, `is_superscript_of`, `is_fraction_numerator`).
2. **Graph Grammar:** We apply a deterministic graph grammar to $G$. The graph is traversed and reduced based on predefined typographic invariants for `pdflatex` math mode, yielding the correct LaTeX syntactic string.

### 3.3 Table Grid Reconstruction

Tables are defined by explicit graphical vectors.

1. **Grid Generation:** Filter the manifold for horizontal and vertical lines. Compute their Cartesian product to identify exact Euclidean intersection points $I = \{ (x_m, y_n) \}$.
2. **Cell Mapping:** Intersections define a discrete grid of rectangular cells $C_{m,n}$. A text node is assigned to $C_{m,n}$ if its geometric centroid falls strictly within the cell boundaries. The matrix is then serialized into Markdown.

### 3.4 Black Box Delegation

Regions devoid of text nodes but bounded by a caption (e.g., `"Fig. X:"`) indicate figures. We apply a maximal empty rectangle algorithm to deduce the contiguous void $V(x_0, y_0, x_1, y_1)$. The exact Euclidean boundaries of $V$ are passed to the `VisionEncoderPort`, encapsulating the external side-effect.

## Chapter 4: The Test-Driven Development (TDD) Axiom

Testing geometric algorithms with physical PDF files is a severe antipattern that couples the pure mathematical domain to filesystem I/O.

All topology and geometry modules must be tested against synthetic geometric manifolds instantiated directly in standard RAM.

```python
def test_synthetic_fraction_topology():
    nodes = [
        SpatialNode(char="1", x0=12.0, y0=10.0, x1=14.0, y1=14.0), # Numerator
        SpatialNode(char="-", x0=10.0, y0=15.0, x1=16.0, y1=16.0), # Fraction line
        SpatialNode(char="2", x0=12.0, y0=17.0, x1=14.0, y1=21.0)  # Denominator
    ]
    # Inject into pure domain morphism and assert structural reduction

```
