# Research Graph Module Formal Specification

## 1. Context and Architectural Paradigm
The `research_graph` module is the discovery and ranking engine of the arXiv scraper. It is responsible for integrating external data sources (arXiv and Semantic Scholar APIs) to construct a localized, directed citation graph $G = (V, E)$.

The module is strictly structured following Hexagonal Architecture principles to enforce the Dependency Inversion Principle (DIP).
* **Domain:** Defines the core data types (Entities) and pure functions (Business Rules).
* **Ports:** Abstract interfaces defining the contracts required by the Domain.
* **Adapters & Infra:** Impure boundary layers where "effectful" computations (I/O, network requests, database transactions) are isolated and executed.

## 2. Definitions: Domain Model and Graph Theory

### Definition 2.1: The Paper Entity (Type)
A paper is defined as an immutable type $P$, represented by the tuple:
$$P = (\text{id}, T, A, \tau, \Sigma)$$
Where:
* $\text{id} \in \mathcal{I}$ is the unique arXiv identifier space.
* $T$ is the title string.
* $A$ is the abstract text.
* $\tau$ is the publication timestamp.
* $\Sigma$ represents auxiliary metadata (e.g., categories, author lists).

### Definition 2.2: The Citation Graph
The discovery process constructs a directed graph $G = (V, E)$.
* The vertex set $V$ consists of papers $v \in V$ such that $v$ maps to a unique $P$.
* The edge set $E \subseteq V \times V$ represents citations. An edge $e = (u, v) \in E$ exists if paper $u$ explicitly cites paper $v$.

### Lemma 2.1: Node Ranking $\mathcal{R}(v)$
To establish the priority of papers for the subsequent ingestion phases, a ranking function $\mathcal{R}: V \to \mathbb{R}$ is applied over the local subgraph $G' \subset G$.

Let $M$ be the adjacency matrix of $G'$. We compute the principal eigenvector $\mathbf{x}$ satisfying:
$$M^T \mathbf{x} = \lambda_{\max} \mathbf{x}$$
The priority rank of paper $v_i$ is defined by the $i$-th component of the normalized eigenvector $\mathbf{x}$, encapsulating the recursive topological importance of the node within the bounded query scope.

## 3. Interfaces (Ports)
To guarantee isolation, the domain must not depend on concrete implementations. We define morphisms (interfaces) using `typing.Protocol`:

1.  **SearchProvider:** Maps a query string to a set of initial vertices $V_{init}$.
2.  **CitationRepository:** Maps a vertex $v$ to a set of adjacent vertices $V_{adj}$ (the edges $E$).

## 4. Effectful Computation (Adapters & Infrastructure)
All side effects are restricted to the outer boundaries of the hexagon.
* **Adapters:** Implement the `SearchProvider` using asynchronous HTTP requests (`httpx`) targeting external APIs.
* **Infrastructure:** Implements the persistence layer using `asyncpg` and `SQLAlchemy`, maintaining the structural integrity of $G$ in an ACID-compliant PostgreSQL database.
