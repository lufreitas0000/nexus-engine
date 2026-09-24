from typing import Protocol, List
from research_graph.src.domain.model import PaperMetadata

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
    async def get_edges(self, arxiv_ids: List[str]) -> List[tuple[str, str]]:
        ...
