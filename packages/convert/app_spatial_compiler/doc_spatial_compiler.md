# App Spatial Compiler: Geometric Reconstruction of 1D Syntactic Trees

## Introduction: The Asymmetry of Computational Cost

In the processing of digital documents, we frequently encounter the problem of state regression. Consider a natively digital PDF generated directly via `pdflatex`. The document is structurally perfect. The Unicode characters and their precise physical bounding boxes exist deterministically in the file's C-level memory.

Transforming this document into a continuous pixel matrix $\mathbb{R}^{H \times W \times C}$ to be processed by a Vision-Language Model (VLM) is a state regression. We intentionally destroy discrete structural data to create a continuous image tensor, forcing the VLM to execute billions of floating-point operations (FLOPS) to approximate data that was already explicitly defined.

The `app_spatial_compiler` module exploits the asymmetry of computational cost when the structural Quality Factor is high ($Q \ge 0.95$). Instead of rendering a tensor, we assume a preprocessing pipeline has executed Direct Memory Access (DMA) to extract a sequence of discrete nodes. We apply deterministic geometric heuristics on the CPU to reconstruct the 1D syntactic tree, requiring $O(N \log N)$ operations and minimal memory footprint.

## Chapter 1: The Domain Models and Memory Contiguity

In our category-theoretic architecture, Objects are Types (Entities) and Morphisms are Pure Functions.

### 1.1 The `BoundingBox` (Input State)

The fundamental Entity is the `BoundingBox`. We assume these entities are provided to the compiler as an initial axiom, having been extracted directly from the `pdflatex` binary streams. They represent text characters, mathematical symbols, and structural lines (e.g., table borders).

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class BoundingBox:
    char: str
    x0: float
    y0: float
    x1: float
    y1: float

```

**Field Definitions:**

* `char`: A Unicode string of length 1 representing the exact character or symbol (e.g., `"A"`, `"\u222B"` for $\int$, or a special token for a graphical line).
* $(x_0, y_0)$: The Euclidean coordinates of the top-left vertex.
* $(x_1, y_1)$: The Euclidean coordinates of the bottom-right vertex.

**Memory Allocation:** Suppressing the dynamic dictionary via `slots=True` ensures the Python interpreter allocates a strict, contiguous memory block. This guarantees spatial locality in the CPU cache during the $O(N \log N)$ Euclidean distance mappings. `frozen=True` ensures mathematical immutability.

### 1.2 The `MarkdownAST` (Output State)

```python
@dataclass(frozen=True, slots=True)
class MarkdownAST:
    content: str
    metadata: dict[str, str]

```

This represents the discrete topological output: a 1D string buffer formatted in Markdown/LaTeX and operational trace data.

## Chapter 2: Structural Subtyping and Dependency Inversion

We define the primary transformations via Python `Protocols` to isolate the Domain logic from Infrastructure side effects.

```python
from collections.abc import Sequence
from typing import Protocol

class SpatialCompilerPort(Protocol):
    def compile_graph(self, nodes: Sequence[BoundingBox]) -> MarkdownAST: ...

class VisionEncoderPort(Protocol):
    def extract_image_context(self, bounds: tuple[float, float, float, float]) -> str: ...

```

When deterministic geometry cannot parse a non-textual graphical region (a figure), the `VisionEncoderPort` is invoked to map the coordinates to an external VLM evaluation.


## Chapter 3: Algorithmic Implementation (Pure Morphisms)

The algorithms are encapsulated within the `GeometricParser`. In our Dependency Inversion architecture, `GeometricParser` is the concrete Domain Service that implements the `SpatialCompilerPort` protocol defined in Chapter 2. It takes a `Sequence[BoundingBox]` and applies pure functional mappings to yield the `MarkdownAST`.

We operate under the assumption that the source is a standard `pdflatex` document. Consequently, the layout follows strict typographic rules that we can exploit mathematically.




### 3.1 Spatial Filtering: Global Invariant Projection Profiles

**Context**
In a standard `pdflatex` document, the spatial placement of headers and footers is globally invariant, governed by the document class geometry. The body text, conversely, is highly variable due to equations, figures, and paragraph breaks. To isolate the body, we must compute the global topological invariants $y_{top}$ and $y_{bottom}$ for the entire document, rather than relying on brittle, per-page heuristic gap thresholds.

**Page Occupancy Function**
Let $N_p$ be the set of all `BoundingBox` entities on a specific page $p$. We define the 1D Boolean occupancy function for page $p$ along the Y-axis as $I_p: \mathbb{R} \to \{0, 1\}$:

$$I_p(y) = \begin{cases} 1 & \exists b \in N_p \text{ such that } b.y_0 \le y \le b.y_1 \\ 0 & \text{otherwise} \end{cases}$$

**Global Occupancy Profile**
Let $P_{sample} \subset P$ be a uniformly random sample of pages from the document. We compute the global horizontal projection profile $O(y)$, which represents the union of all occupied vertical spaces across the sample:

$$O(y) = \bigvee_{p \in P_{sample}} I_p(y)$$

**Invariant Margin Null-Spaces**
In a structurally uniform document, the header and footer are separated from the body text by vertical bands of empty space that are absolutely invariant across all pages. Therefore, the function $O(y)$ will contain continuous intervals $[y_a, y_b]$ where $O(y) = 0$, completely isolating the header/footer regions from the dense core where $O(y) = 1$.

**Algorithm (Deterministic Margin Extraction)**
We replace subjective constants with a pure geometric intersection algorithm over $O(y)$:

1. **Sampling and Projection:** Randomly sample $k$ pages (e.g., $k=10$). Compute the discrete array representing $O(y)$ by projecting all $y_0$ and $y_1$ coordinates.
2. **Gap Extraction:** Identify all continuous intervals $G_i = [y_{start}, y_{end}]$ where $O(y) = 0$.
3. **Median Font Height ($\tilde{h}$):** To filter out microscopic topological noise (e.g., fractional spaces between superscripts and standard text), compute the median bounding box height $\tilde{h}$ across the sample.
4. **Margin Identification:**
* Filter the set of gaps to retain only macroscopic gaps: $G_{macro} = \{ G_i \mid (y_{end} - y_{start}) > 2\tilde{h} \}$.
* The top margin separator is the uppermost macroscopic gap. We set $y_{top}$ to the bottom edge of this gap: $y_{top} = \max(y) \text{ for } y \in G_{top}$.
* The bottom margin separator is the lowermost macroscopic gap. We set $y_{bottom}$ to the top edge of this gap: $y_{bottom} = \min(y) \text{ for } y \in G_{bottom}$.



**Connections and Reflections**
By applying the Boolean projection $\bigvee I_p(y)$ globally, we project out the high-frequency spatial noise generated by localized subscripts, superscripts, and inline equations. A local equation only expands $I_p(y)$ for a single page $p$, which is absorbed seamlessly into the global profile without affecting the invariant margin null-spaces. Consequently, for any given page, the true body subset is strictly defined by the pure filtering morphism:

$$N_{body} = \{ b \in N_p \mid y_{top} < b.y_0 \land b.y_1 < y_{bottom} \}$$

This establishes an exact, deterministically proven bounding manifold for the downstream paragraph and equation clustering algorithms, devoid of subjective constants like $k \ge 3.0$.




### 3.2 Baseline Clustering (Paragraphs)

With $N_{body}$ isolated, we project the 2D spatial nodes onto the Y-axis. We group entities into a single line $l_k$ if their vertical baselines $y_0$ are within a strict font tolerance $\epsilon_{font}$.

$$l_k = \{ b_i \in N_{body} \mid |b_i.y_0 - \mu_{y}(l_k)| < \epsilon_{font} \}$$

We compute the vertical displacement between consecutive body lines: $\Delta y = y_0(l_{k+1}) - y_1(l_k)$.

* If $\Delta y \approx \tilde{g}$ (the median gap), the lines form a continuous paragraph block.
* If $\Delta y > 1.5 \cdot \tilde{g}$ (standard paragraph separation), we inject a double newline `\n\n` to break the Markdown paragraph.

### 3.3 Mathematical Formulation (Equations)

Equations present local topological anomalies compared to standard text. We classify them geometrically:

1. **Display Mode Detection:** If a sequence of nodes $E \subset N_{body}$ possesses a large left margin displacement ($E.x_0 \gg \text{page\_margin}$) and contains high-density Unicode math operators ($\sum, \int$), we classify it as an equation and wrap the parsed string in `$$...$$`.
2. **Equation Numbering:** `pdflatex` strictly right-aligns equation numbers. If we detect a bounding box sequence matching the regular expression `^\(\d+\)$` located at $x_1 \approx \text{page\_width}$, we map it to the LaTeX `\tag{n}` macro.
3. **Fractions:** If an abnormally wide horizontal node (the fraction line code point) is detected, we compute geometric bounding box intersections. We partition local nodes into a numerator subset (nodes strictly above $y_0$ of the line) and a denominator subset (nodes strictly below $y_1$ of the line), yielding `\frac{num}{den}`.

### 3.4 Table Grid Reconstruction

Tables in `pdflatex` are defined by explicit horizontal and vertical graphical lines (vectors).

1. **Grid Generation:** We filter $N_{body}$ for line entities. We compute the Cartesian product of horizontal and vertical line segments to identify exact Euclidean intersection points $I = \{ (x_m, y_n) \}$.
2. **Cell Mapping:** These intersections define a discrete grid of rectangular cells $C_{m,n}$. For every text `BoundingBox` in the table's spatial domain, we calculate its geometric centroid.
3. **Assignment:** The node is mapped to cell $C_{m,n}$ if its centroid falls strictly within the cell's boundaries. The filled grid is serialized into Markdown table syntax.

### 3.5 Figures and Black Box Delegation

Figures in `pdflatex` manifest as macroscopic regions devoid of text nodes, usually bounded by a text sequence starting with `"Figure X:"` or `"Fig. X:"`.

1. **Empty Space Deduction:** We apply a maximal empty rectangle algorithm (a sweep-line approach over the bounding boxes) to identify the largest contiguous void $V(x_0, y_0, x_1, y_1)$ immediately adjacent to a detected caption.
2. **Delegation:** We pass the exact Euclidean boundaries of $V$ to the `app_vision_encoder` interface. This encapsulates the external side-effect (the VLM execution) behind the `VisionEncoderPort`, ensuring the `GeometricParser` remains purely mathematical.





## Chapter 4: The Test-Driven Development (TDD) Axiom

Testing geometric algorithms with physical PDF files is a severe antipattern. It couples the pure mathematical domain to filesystem I/O.

### 4.1 Synthetic Geometric Manifolds

In our `pytest` suite, we construct synthetic arrays of `BoundingBox` objects directly in standard RAM. To test the fraction algorithm, we instantiate:

```python
nodes = [
    BoundingBox(char="1", x0=12.0, y0=10.0, x1=14.0, y1=14.0), # Numerator
    BoundingBox(char="-", x0=10.0, y0=15.0, x1=16.0, y1=16.0), # Fraction line
    BoundingBox(char="2", x0=12.0, y0=17.0, x1=14.0, y1=21.0)  # Denominator
]

```

We inject this sequence into the `GeometricParser` and mathematically assert that the output string matches `\frac{1}{2}`.
