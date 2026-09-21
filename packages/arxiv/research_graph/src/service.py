from typing import Set
import asyncio

from research_graph.ports.interfaces import SearchProvider, CitationProvider
from research_graph.infra.uow import PostgresUnitOfWork

async def expand_query_graph(
    query: str,
    search_provider: SearchProvider,
    citation_provider: CitationProvider,
    uow: PostgresUnitOfWork
) -> Set[str]:
    # 1. Retrieve initial vertices V_init
    initial_papers = await search_provider.search_by_query(query, max_results=50)
    initial_ids = {paper.arxiv_id for paper in initial_papers}

    # Save initial papers to DB
    async with uow:
        if uow.papers:
            for paper in initial_papers:
                await uow.papers.save_paper(paper)
        await uow.commit()

    # 2. Map citation retrieval over V_init to find V_adj
    # Limit concurrency to be polite to the API
    semaphore = asyncio.Semaphore(5)

    adjacent_ids = set()

    async def fetch_and_save_citations(arxiv_id: str):
        async with semaphore:
            try:
                citations = await citation_provider.get_citations(arxiv_id)

                # Save edges
                # Each task needs its own uow context. But we are sharing the same PostgresUnitOfWork instance.
                # UOW manages state (session). It is not thread/task-safe to use concurrently without a new session.
                # We need a new session per task, or we should collect all edges and save them in one go outside
                # the concurrent tasks.
                # Let's return the edges and save them outside.
                return arxiv_id, citations
            except Exception as e:
                # Log error and continue
                print(f"Error fetching citations for {arxiv_id}: {e}")
                return arxiv_id, []

    # Run concurrently
    tasks = [fetch_and_save_citations(arxiv_id) for arxiv_id in initial_ids]
    results = await asyncio.gather(*tasks)

    async with uow:
        for arxiv_id, citations in results:
            adjacent_ids.update(citations)
            if uow.papers:
                for cited_id in citations:
                    await uow.papers.save_edge(arxiv_id, cited_id)
        await uow.commit()

    return initial_ids.union(adjacent_ids)
