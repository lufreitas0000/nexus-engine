# Research Graph Module Specification

The `research_graph` module is the discovery and ranking engine of the arXiv scraper. Its purpose is to integrate external data sources to construct a localized, directed citation graph, evaluate the topological importance of each node, and persist this structure for downstream processing.

The infrastructure layer encapsulates all "effectful" operations, such as network I/O and database transactions, isolating side effects from the domain.

---

## 1. Domain Model and Graph Topology


#### The Paper Entity

A scientific paper is modeled as an immutable data structure. Let $P$ be a paper defined by the tuple $P = (\text{id}, T, A, \tau, \Sigma)$, where $\text{id}$ is the unique arXiv identifier, $T$ is the title, $A$ is the abstract, $\tau$ is the publication date string formatted as `YYYYMMDD`, and $\Sigma$ represents auxiliary metadata (e.g., authors). The simplification of the timestamp guarantees domain equivalence without timezone overhead.

Python

```
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PaperMetadata:
    arxiv_id: str
    title: str
    abstract: str
    published_date: str  # Format: YYYYMMDD
    authors: List[str]
```

#### The Citation Graph and Topological Ranking

The discovery process constructs a directed graph $G = (V, E)$. To constrain the computational complexity, the vertex set $V$ is strictly bounded to a depth-1 expansion. Let $V_{init}$ be the set of papers returned by the initial arXiv query. The total universe of vertices is $V = V_{init} \cup \{v \mid (u, v) \in E \lor (v, u) \in E \text{ for } u \in V_{init}\}$. We only analyze the topology within this closed universe of known IDs stored in the SQL database.

Let $A$ be the adjacency matrix of size $|V| \times |V|$ for this subgraph, where $A_{ij} = 1$ if paper $v_i$ cites paper $v_j$ (a directed edge $v_i \to v_j$), and $A_{ij} = 0$ otherwise.

To compute the priority score of each paper, we utilize Eigenvector Centrality. We solve the eigenvalue equation for the transposed adjacency matrix:

$$A^T \mathbf{x} = \lambda \mathbf{x}$$

**Mathematical Interpretation:**

The matrix $A^T$ transfers "authority". The $j$-th component of the operation $A^T \mathbf{x}$ is exactly $\sum_i A_{ij} x_i$. Therefore, the centrality score of paper $v_j$ is proportional to the sum of the centrality scores of all papers $v_i$ that cite it.

By the Perron-Frobenius theorem, assuming an irreducible non-negative matrix (often achieved by adding a small damping factor $d > 0$ to all entries to simulate a complete graph, ensuring the graph is strongly connected), there exists a unique principal eigenvector $\mathbf{x}$ associated with the strictly maximal real eigenvalue $\lambda_{\max}$.

The $i$-th component $x_i$ of the normalized principal eigenvector $\mathbf{x}$ is the priority score of paper $v_i$. A higher priority score strictly implies that $v_i$ is heavily cited by other highly central papers _specifically within the context of the initial query_.
---

## 2. Ports (Interfaces)

The domain dictates the contracts required to fetch data. We define these interfaces using `typing.Protocol` to ensure structural subtyping without coupling the domain to concrete implementations.

```python
from typing import Protocol, List

class SearchProvider(Protocol):
    async def search_by_query(self, query: str, max_results: int) -> List[PaperMetadata]:
        """Maps a query string to an initial set of vertices V_init."""
        ...

class CitationProvider(Protocol):
    async def get_citations(self, arxiv_id: str) -> List[str]:
        """Maps a vertex v to a set of adjacent vertices (arXiv IDs) representing outgoing edges."""
        ...

class GraphRepository(Protocol):
    async def save_paper(self, paper: PaperMetadata) -> None:
        ...
    async def save_edge(self, citing_id: str, cited_id: str) -> None:
        ...
```


#### Port Composition: Discovery Pipeline

The Application Service orchestrates the discovery by composing the `SearchProvider` and `CitationProvider` functions. Let $f_S: \text{Query} \to V_{init}$ be the search function and $f_C: \text{ID} \to V_{adj}$ be the citation retrieval function.

The execution yields the complete set of relevant identifiers by extracting the IDs from $V_{init}$ and mapping them over $f_C$.


```python
async def expand_query_graph(
    query: str,
    search_provider: SearchProvider,
    citation_provider: CitationProvider
) -> set[str]:
    # 1. Retrieve initial vertices V_init
    initial_papers = await search_provider.search_by_query(query, max_results=50)
    initial_ids = {paper.arxiv_id for paper in initial_papers}

    # 2. Map citation retrieval over V_init to find V_adj
    # Note: In production, this must be bounded by asyncio.gather with a semaphore.
    adjacent_ids = set()
    for arxiv_id in initial_ids:
        citations = await citation_provider.get_citations(arxiv_id)
        adjacent_ids.update(citations)

    return initial_ids.union(adjacent_ids)
```



---

## 3. Adapters (External APIs)

The adapters implement the defined protocols by performing effectful HTTP requests. We utilize `httpx.AsyncClient` to handle asynchronous network I/O, allowing concurrent connections without blocking the main event loop.

### arXiv API Adapter

**Semantics:** The arXiv API exposes an Atom/XML feed. It is used to map a domain query to initial paper metadata.

* **Input:** Search query and pagination parameters.
* **Endpoint:** `http://export.arxiv.org/api/query?search_query={query}&max_results={n}`
* **Output:** XML payload containing `<entry>` tags with `<id>`, `<title>`, `<summary>`, and `<author>` fields.

```python
import httpx
import xml.etree.ElementTree as ET

class ArxivAdapter:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = "[http://export.arxiv.org/api/query](http://export.arxiv.org/api/query)"

    async def search_by_query(self, query: str, max_results: int) -> List[PaperMetadata]:
        params = {"search_query": query, "max_results": max_results}
        response = await self.client.get(self.base_url, params=params)
        response.raise_for_status()
        return self._parse_xml_to_domain(response.text)

    def _parse_xml_to_domain(self, xml_text: str) -> List[PaperMetadata]:
        # XML parsing logic extracting namespaces and mapping to PaperMetadata
        pass
```

### Semantic Scholar API Adapter

**Semantics:** The Semantic Scholar Graph API is used to traverse the citation edges. By querying a specific arXiv ID, we retrieve the references (what the paper cites) and citations (who cites the paper).

* **Input:** The arXiv ID of a known vertex.
* **Endpoint:** `https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}?fields=citations,references`
* **Output:** JSON payload containing arrays of paper objects with their respective identifiers.

```python
class SemanticScholarAdapter:
    def __init__(self, client: httpx.AsyncClient, api_key: str = None):
        self.client = client
        self.headers = {"x-api-key": api_key} if api_key else {}
        self.base_url = "[https://api.semanticscholar.org/graph/v1/paper/arXiv](https://api.semanticscholar.org/graph/v1/paper/arXiv):"

    async def get_citations(self, arxiv_id: str) -> List[str]:
        url = f"{self.base_url}{arxiv_id}?fields=citations"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        # Extract arXiv IDs from the response JSON
        return [
            item["arxivId"] for item in data.get("citations", [])
            if item.get("arxivId") is not None
        ]
```

---

## 4. Infrastructure (Persistence Layer)

To persist the citation graph, we implement a PostgreSQL database using `asyncpg` as the asynchronous driver and SQLAlchemy 2.0 for the Object-Relational Mapping (ORM).

### Schema Design

* **Papers Table:** Stores the vertex data $P$. The `arxiv_id` is the primary key, ensuring idempotency across multiple API traversals.
* **Citations Table:** An association table representing the edges $E$. It forms a many-to-many self-referential relationship mapping `referrer_id` to `referee_id`.

```python
from sqlalchemy import Column, String, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

citation_table = Table(
    "citations",
    Base.metadata,
    Column("referrer_id", String, ForeignKey("papers.arxiv_id"), primary_key=True),
    Column("referee_id", String, ForeignKey("papers.arxiv_id"), primary_key=True),
)

class PaperORM(Base):
    __tablename__ = "papers"

    arxiv_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text)
    published_date: Mapped[datetime] = mapped_column(DateTime)

    citations: Mapped[List["PaperORM"]] = relationship(
        "PaperORM",
        secondary=citation_table,
        primaryjoin=arxiv_id == citation_table.c.referrer_id,
        secondaryjoin=arxiv_id == citation_table.c.referee_id,
        back_populates="cited_by",
    )

    cited_by: Mapped[List["PaperORM"]] = relationship(
        "PaperORM",
        secondary=citation_table,
        primaryjoin=arxiv_id == citation_table.c.referee_id,
        secondaryjoin=arxiv_id == citation_table.c.referrer_id,
        back_populates="citations",
    )

```


#### Relational Mapping and Association Tables

In the SQLAlchemy schema, `citation_table` is defined as a Core `Table` rather than a Declarative `class`. In the ORM paradigm, classes represent entities with identity and lifecycle. The `citation_table` is a pure association table representing the edges $E \subseteq V \times V$. It contains no payload data other than the foreign keys forming its composite primary key. SQLAlchemy's `relationship()` construct implicitly manages these pure association tables, rendering a dedicated class unnecessary and structurally redundant.

#### Unit of Work (UoW) Pattern

The `AsyncSession` from SQLAlchemy naturally implements the Unit of Work pattern. It maintains an in-memory ledger of all objects loaded, modified, or queued for insertion within a given scope. To formally enforce the Dependency Inversion Principle, we abstract the database transaction boundary.

The UoW acts as a context manager that provides access to the `GraphRepository` and strictly manages the atomic commit or rollback of the transaction, ensuring the ACID properties of the graph $G$ upon insertion.



```python
from typing import Protocol
from types import TracebackType

class UnitOfWork(Protocol):
    papers: GraphRepository

    async def __aenter__(self) -> 'UnitOfWork':
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
```

---


## 5. Quality Assurance and Testing Architecture

To guarantee the deterministic behavior of the domain and the resilience of the effectful boundaries, the module enforces strict testing and static analysis protocols.

## Static Analysis

- **Type Checking:** `mypy --strict` is enforced. The domain logic must maintain absolute type stability without relying on `Any`.

- **Linting:** Code formatting and import sorting are managed by `ruff` or `flake8` to maintain mathematical conciseness in the codebase.


## Testing Strategy

The test suite utilizes `pytest` and `pytest-asyncio`. Tests are segregated into Unit Tests (Domain & Application) and Integration Tests (Adapters & Infrastructure).

1. **Mocking Network Boundaries:** The `httpx` asynchronous calls within the Adapters are intercepted using `respx`. This prevents actual network egress during testing and allows deterministic injection of mock XML/JSON payloads.

2. **Infrastructure Integration:** The `PostgresGraphRepository` is tested against an ephemeral, isolated PostgreSQL instance spun up via Docker (using `pytest-docker` or Testcontainers). This guarantees that SQL constraints (like the composite primary key on the `citation_table`) execute correctly.

3. **Fixtures (`conftest.py`):**

    - `db_session`: Yields an SQLAlchemy `AsyncSession` bound to the test database, rolling back after each test to ensure state isolation.

    - `mock_arxiv_xml`: Provides a byte string of a valid arXiv API response.

    - `mock_semantic_scholar_json`: Provides a dictionary representing the citation graph response.
