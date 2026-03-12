
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

Before we subject a PDF to a heavy, computationally expensive Vision-Language Model for OCR (Optical Character Recognition), we must understand its physical layout.

Is the PDF a scanned image of a book (raster), or is it a modern digital document where the text is already stored as computer-readable characters (vector)?

**The Optimization Goal:**
Eventually, we will need to perform OCR regardless to extract complex LaTeX equations and tables, and we will need vision models to generate ALT text for figures. However, if the main body text is already digitally present in the PDF, we want to extract it directly. Running full-page OCR on a 500-page book that already contains structured text is a massive waste of computational resources. The classifier helps us optimize the pipeline: if text exists, we simply reorganize it; if it is trapped in an image, we invoke the heavy OCR models.

**Metadata and Fonts:**
PDFs contain internal dictionaries, known as the XREF table. Using libraries like `PyMuPDF`, we can inspect this metadata. If a document uses digital text, it will reference Font dictionaries (like Arial or Times New Roman). If it is a scan, it will primarily reference Image objects. Looking at this metadata gives us a fast clue about the document type without reading the whole file.

However, metadata can be deceptive. Sometimes, a PDF contains digital fonts, but the mapping to standard characters (the ToUnicode table) is broken or intentionally obfuscated. Extracting the text yields garbage characters.

**The Shannon Entropy Heuristic:**
To definitively prove if the text is readable, we sample a page and evaluate it using Information Theory—specifically, Shannon Entropy.

Entropy measures the unpredictability or "surprise" of a sequence. For a string of characters extracted from the document, let $X$ be the sequence of characters. The zeroth-order Shannon Entropy $H(X)$ is computed as:

$$H(X) = -\sum_{x \in \Sigma} P(x) \log_2 P(x)$$

*How we compute $P(x)$:*
We take the extracted string and count how many times each character appears. We divide that count by the total length of the string to get the probability $P(x)$ of that character occurring.

*Why is it bounded?*
In standard natural language (like English), characters do not appear randomly. Vowels like 'e' and 'a' appear very frequently, while 'z' and 'q' are rare. This predictable unevenness (known as a Zipfian distribution) means the entropy of natural language is mathematically bounded, typically falling between:

$$3.5 \leq H_{text}(X) \leq 5.0 \text{ bits/character}$$

If we try to extract text from a pure scanned image, we get nothing, or highly repetitive blank spaces. The entropy drops toward $0.0$. If the PDF contains encrypted text or we mistakenly read raw image bytes as characters, the data is completely random, and the entropy spikes toward the maximum limit of an 8-bit system ($8.0$).

**Pros, Cons, and Alternatives:**

* *Pros:* Computing entropy is incredibly fast ($O(1)$ compared to reading the whole book) and mathematically rigorous.
* *Cons:* It is statistical. If we sample a page that happens to be entirely a complex mathematical table with obscure symbols, the entropy might artificially spike outside our bounds.
* *Alternatives:* We could train a small machine learning classifier to look at the page, but that introduces unnecessary weight. We could rely purely on the XREF font metadata, but as mentioned, that fails on obfuscated PDFs.

In our code, if the calculated $H(X)$ falls within `[3.5, 5.0]`, we assign a Quality Factor of `1.0`, mathematically guaranteeing that we can safely extract the digital text and save massive GPU resources.

**Testing Topology:**
We test this by passing our synthetic "degraded raster" PDF (which yields an entropy near 0) and our "clean vector" PDF (which yields natural language entropy). The test proves the math works reliably on both extremes.

## Chapter 5: The Infrastructure Adapter

This is where our pure mathematics hits the physical hardware. The `MarkerVisionAdapter` is the concrete implementation that loads the real machine learning models (like `marker-pdf` and PyTorch).

**Lazy Loading:**
Machine Learning models are massive arrays of floating-point numbers. If we loaded PyTorch at the very top of our script, the Python interpreter would immediately allocate gigabytes of RAM the moment the application booted—even if the user only wanted to access a `--help` menu in the terminal.

To prevent this, we use Lazy Loading. The neural network weights are only moved into the computer's memory at the exact millisecond the user actually requests an extraction.

**Testing the Infrastructure:**
Because this adapter requires heavy libraries and potentially a GPU, we explicitly isolate it. In our standard testing environment, we use the command-line flag `--use-fake` to bypass this adapter entirely, ensuring our CI/CD pipelines run smoothly without requiring specialized hardware.
