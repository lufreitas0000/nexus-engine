import pytest
import asyncio
from typing import List

from research_graph.domain.model import PaperMetadata
from research_graph.ports.interfaces import SearchProvider, CitationProvider
from research_graph.src.service import expand_query_graph
from research_graph.infra.uow import PostgresUnitOfWork
from research_graph.tests.test_infra import sqlite_engine, session_factory

class MockSearchProvider(SearchProvider):
    async def search_by_query(self, query: str, max_results: int) -> List[PaperMetadata]:
        return [
            PaperMetadata("1", "A", "A", "20230101", []),
            PaperMetadata("2", "B", "B", "20230101", [])
        ]

class MockCitationProvider(CitationProvider):
    async def get_citations(self, arxiv_id: str) -> List[str]:
        if arxiv_id == "1":
            return ["3", "4"]
        if arxiv_id == "2":
            return ["4", "5"]
        return []

@pytest.mark.asyncio
async def test_expand_query_graph(session_factory):
    uow = PostgresUnitOfWork(session_factory)
    search_prov = MockSearchProvider()
    citation_prov = MockCitationProvider()

    all_ids = await expand_query_graph("test", search_prov, citation_prov, uow)

    assert all_ids == {"1", "2", "3", "4", "5"}

    # Check DB
    async with uow:
        # Just manually verifying it didn't crash and we can access uow
        pass
