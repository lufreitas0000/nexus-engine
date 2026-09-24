# Architecture Note: PDF Optimization Submodule (Phase 3)

## Context

Standard academic PDFs generated via LaTeX (specifically A4 or US Letter physical formats) construct fixed-coordinate layout matrices. These matrices bind typographic glyphs to absolute Cartesian coordinates on a virtual page. This structural paradigm is highly sub-optimal for 7-inch e-ink displays, leading to severe usability degradation. Forcing an A4 fixed layout onto a 7-inch matrix requires continuous horizontal and vertical panning (pan-and-scan), which introduces an unacceptable cognitive load when parsing dense scientific literature.

The objective of Phase 3 is to geometrically restructure these documents for the Kindle Oasis hardware matrix without destroying the vector-based rendering of complex mathematical structures. Semantic parsing of advanced physics notation must remain structurally intact and mathematically rigorous.

## Definition: The Raster-Reflow Algorithm

Standard conversion algorithms (e.g., generic PDF to EPUB pipelines relying on `pdftohtml` or similar heuristic engines) attempt to parse absolute Cartesian coordinate glyphs back into a semantic Document Object Model (HTML/MathML). This heuristic approach deterministically fails on advanced mathematics because spatial relationships (e.g., a limit subscript positioned specifically under a summation integral) are lost during the linear semantic extraction.

Instead, we employ `k2pdfopt`, a specialized tool that bypasses semantic extraction entirely by operating via computer vision. It applies a raster-reflow algorithm. First, it renders the source PDF pages into high-resolution bitmaps. Next, it utilizes connected-component analysis and whitespace thresholding to identify contiguous bounding boxes containing discrete logical units (paragraphs, standalone equations, data tables, and figures). Finally, it re-wraps these discrete image blocks into a new PDF sequence constrained strictly by the target device's pixel matrix. Because it manipulates blocks of pixels rather than attempting to map fonts to Unicode characters, this algorithm guarantees 100% visual fidelity of all mathematical notation.

## Structural Constraints (Hexagonal Architecture)

The submodule is strictly orthogonal and adheres to the Dependency Inversion principle. To maintain testability and operational safety, the effectful computations—specifically the `k2pdfopt` subprocess call and filesystem I/O operations—are strictly isolated in the Infrastructure layer.

- **`/src/domain/`**: Defines the pure data structures and configuration schemas (`TargetHardwareConstraints`, `OptimizerConfig`). This layer contains zero I/O operations and dictates the mathematical rules of the pipeline.

- **`/src/services/`**: Contains the pure pipeline orchestration logic mapping the input binary stream to the optimized output binary stream. It relies entirely on dependency injection for filesystem interactions.

- **`/src/infra/`**: Houses the concrete adapters. This includes the `subprocess` wrapper for the `k2pdfopt` system binary execution and the `pypdf` adapter for transient chunk manipulation and metadata extraction.

- **`/tests/`**: Implements deterministic, mock-driven validation of the isolated modules, allowing the pipeline to be verified in CI/CD environments where the `k2pdfopt` binary may not be natively compiled.


## Hardware Mapping & Native Configuration

Rather than manually forcing font sizing via unreliable geometric scaling, we leverage `k2pdfopt`'s native spatial optimization algorithms to automatically maximize readability on the Kindle Oasis. The configuration translates into deterministic CLI parameters as follows:

1. **Device Matrix**: The layout is mathematically constrained to the physical Oasis hardware limits (`-w 1264 -h 1680 -dpi 300`). Setting the exact DPI ensures the rasterization engine does not artificially oversample or undersample the source bounding boxes.

2. **Margin Processing**: We utilize the native auto-crop algorithm (`-m 0.2`) to dynamically eliminate static whitespace. This algorithm scans the pixel density of the document edges, crops the empty gutters, and centers the text bounding boxes, effectively utilizing 100% of the e-ink display area.

3. **Column Flattening**: Academic papers frequently utilize two-column layouts. The engine natively detects the vertical whitespace of column gutters (`-col`) and sequentializes multi-column papers into a continuous, single-column vertical flow (`-wrap`). It utilizes reading-order heuristics to ensure left-column blocks are ordered before right-column blocks.

4. **Header/Footer Pruning**: Static repetitive metadata (e.g., ArXiv timestamps, journal publication margins, page numbers) are algorithmically ignored using native clear-box/ignore-margin parameters. This prevents static headers from interrupting the logical flow of the reflowed text mid-sentence.


## Operational Pipeline ($N$-Stage Morphism)

The optimization function $f(x) \rightarrow y$ (where $x$ is the input PDF and $y$ is the optimized artifact) is executed via a deterministic, multi-stage pipeline designed to prevent memory leaks, manage heap allocation, and handle highly variable document lengths ranging from $O(10)$ to $O(100)$ pages.

### Stage 1: Pre-Validation

- **Integrity Check**: Read the initial byte header of the payload to verify the standard `%PDF` magic number, ensuring the input is not a malformed or disguised binary.

- **Filesystem State**: Verify the input file size $> 0$ bytes and strictly validate the existence of POSIX read permissions before allocating memory.


### Stage 2: Pre-Processing

- **Metadata Extraction**: The raster-reflow algorithm operates on bitmaps and consequentially strips the original PDF's `/Info` dictionary. We extract Dublin Core equivalents (Title, Author) via `pypdf` prior to rasterization and cache them in system memory.

- **Chunk Generation**: To prevent subprocess timeouts on dense documents, calculate the total page count $P$. Define a constant constraint $C$ (e.g., 20 pages). Partition the binary stream into $N = \lceil P/C \rceil$ discrete temporary chunks. For example, a 45-page document will yield three distinct chunks ($20, 20, 5$).


### Stage 3: Subprocess Execution (Infrastructure)

- Iterate over the $N$ chunks sequentially, mapping them to isolated `k2pdfopt` subprocess calls.

- Enforce a deterministic execution timeout $T$ per chunk (calculated as $T = C \times \text{timeout\_per\_page\_constant}$). If an isolated instance hangs due to an unresolvable complex geometric array, the pipeline raises a controlled exception and halts execution rather than blocking system threads indefinitely.


### Stage 4: Post-Processing

- **Artifact Merging**: Concatenate the successfully reflowed $N$ chunks back into a single, contiguous binary sequence using the `pypdf` merger object.

- **Metadata Re-Injection**: Write the memory-cached Title and Author back into the `/Info` dictionary of the newly merged artifact. This step is critical; failure to append this metadata deterministically triggers an Amazon E999 internal ingestion error during SMTP dispatch.

- **Garbage Collection**: Execute an atomic `unlink` on all transient chunk files from the temporary filesystem directory to prevent storage exhaustion across multiple pipeline executions.


### Stage 5: Post-Validation

- **Structural Verification**: Verify the final concatenated artifact size $> 0$ bytes to ensure the merge operation did not yield a null pointer or empty buffer.

- **Termination Marker**: Validate the presence of the `%%EOF` (End Of File) marker at the absolute tail of the binary sequence. This ensures the PDF trailer dictionary was written correctly and the file will not corrupt upon device transfer.


## Corollaries

- **Footnotes**: In a raster-reflowed matrix, dynamic hyperlinking is impossible. `k2pdfopt` treats footnote boundary separators as standard horizontal structural blocks. It appends the footnote text inline at the bottom of the virtual page. While this alters standard typographic flow, it guarantees zero loss of academic citation data.

- **Asynchronous Potential**: Future iterations of Stage 3 can map the $N$ chunks to a Python `multiprocessing` pool to parallelize the rasterization workload across multiple CPU cores, drastically reducing the temporal complexity of the compilation phase for larger textbook-scale documents.




---


Critical system-level edges that require explicit definition.
Addressing these now will prevent race conditions, memory leaks, and deployment failures during the implementation of the chunked raster-reflow pipeline.

### 1. External Binary Resolution (The `$PATH` Constraint)
The pipeline relies on the `k2pdfopt` system binary.
* **The Issue:** `subprocess.run` relies on the host OS environment variables to locate executables. If the binary is not globally accessible in the `$PATH`, the pipeline will fail immediately (similar to the historical Pandoc error).
* **The Proposition:** Should we hardcode the execution vector to assume `k2pdfopt` is in the `$PATH`, or should we abstract the binary path into the `.env` configuration (e.g., `K2PDFOPT_PATH=/usr/local/bin/k2pdfopt`) with a default fallback? Abstracting it increases environment portability.

### 2. Transient State and Atomic Garbage Collection
The $N$-stage chunking architecture introduces significant disk I/O. A 100-page PDF divided into 5 chunks will generate 5 input temporary files and 5 output temporary files before merging.
* **The Issue:** If a `KeyboardInterrupt` occurs, or if chunk 3 fails due to a `subprocess.TimeoutExpired`, the pipeline must not leave orphaned binary artifacts on the filesystem (preventing inode exhaustion).
* **The Proposition:** The transient chunks must be generated within a unified `tempfile.TemporaryDirectory` context manager, rather than individual `NamedTemporaryFile` calls. This ensures the Python runtime automatically executes an atomic recursive deletion of the directory upon context exit, regardless of success or exception states.

### 3. Concurrency and Sequence Preservation
If we implement asynchronous or parallel execution for Stage 3 (Subprocess Execution) to reduce temporal complexity:
* **The Issue:** Asynchronous execution does not guarantee order of completion. Chunk 4 might finish rasterizing before Chunk 2.
* **The Proposition:** The intermediate chunks must be strictly indexed (e.g., `chunk_001.pdf`, `chunk_002.pdf`). The merging mechanism (`pypdf.PdfMerger`) must independently sort the target artifacts by this index before concatenation, strictly decoupling execution order from structural order.

### 4. Dependency Manifest Update
The Phase 3 architecture introduces a new required dependency for metadata extraction and binary merging.
* **The Proposition:** We must append `pypdf` to `requirements.in` and execute `pip-compile requirements.in` to lock the deterministic hash in `requirements.txt`.
