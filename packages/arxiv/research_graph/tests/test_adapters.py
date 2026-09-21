import pytest
import httpx
import respx
from research_graph.adapters.external_apis import ArxivAdapter, SemanticScholarAdapter

ARXIV_XML_MOCK = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2101.00001v1</id>
    <published>2021-01-01T00:00:00Z</published>
    <title>Test Paper Title</title>
    <summary>Test abstract.</summary>
    <author>
      <name>John Doe</name>
    </author>
    <author>
      <name>Jane Doe</name>
    </author>
  </entry>
</feed>
"""

SEMANTIC_SCHOLAR_JSON_MOCK = {
    "citations": [
        {"arxivId": "2101.00002"},
        {"arxivId": "2101.00003"},
        {"arxivId": None} # Should be ignored
    ]
}

@pytest.mark.asyncio
async def test_arxiv_adapter():
    async with httpx.AsyncClient() as client:
        adapter = ArxivAdapter(client)

        with respx.mock(assert_all_called=False) as respx_mock:
            respx_mock.get("http://export.arxiv.org/api/query?search_query=all:electron&max_results=1").mock(return_value=httpx.Response(200, text=ARXIV_XML_MOCK))

            papers = await adapter.search_by_query("all:electron", 1)

            assert len(papers) == 1
            assert papers[0].arxiv_id == "2101.00001v1"
            assert papers[0].title == "Test Paper Title"
            assert papers[0].abstract == "Test abstract."
            assert papers[0].published_date == "20210101"
            assert papers[0].authors == ["John Doe", "Jane Doe"]

@pytest.mark.asyncio
async def test_semantic_scholar_adapter():
    async with httpx.AsyncClient() as client:
        adapter = SemanticScholarAdapter(client)

        with respx.mock(assert_all_called=False) as respx_mock:
            respx_mock.get("https://api.semanticscholar.org/graph/v1/paper/arXiv:2101.00001v1?fields=citations").mock(return_value=httpx.Response(200, json=SEMANTIC_SCHOLAR_JSON_MOCK))

            citations = await adapter.get_citations("2101.00001v1")

            assert len(citations) == 2
            assert "2101.00002" in citations
            assert "2101.00003" in citations
