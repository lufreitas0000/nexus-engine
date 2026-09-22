import httpx
import xml.etree.ElementTree as ET
from typing import List, Optional

from research_graph.domain.model import PaperMetadata

class ArxivAdapter:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = "https://export.arxiv.org/api/query"

    async def search_by_query(self, query: str, max_results: int) -> List[PaperMetadata]:
        params = {"search_query": query, "max_results": max_results}
        response = await self.client.get(self.base_url, params=params)
        response.raise_for_status()
        return self._parse_xml_to_domain(response.text)

    def _parse_xml_to_domain(self, xml_text: str) -> List[PaperMetadata]:
        root = ET.fromstring(xml_text)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}

        papers = []
        for entry in root.findall("atom:entry", namespace):
            id_element = entry.find("atom:id", namespace)
            arxiv_id = id_element.text.split("/abs/")[-1] if id_element is not None and id_element.text else ""

            title_element = entry.find("atom:title", namespace)
            title = title_element.text.strip().replace("\n", " ") if title_element is not None and title_element.text else ""

            summary_element = entry.find("atom:summary", namespace)
            abstract = summary_element.text.strip().replace("\n", " ") if summary_element is not None and summary_element.text else ""

            published_element = entry.find("atom:published", namespace)
            # Example format: 2024-03-15T12:00:00Z -> 20240315
            published_date = published_element.text[:10].replace("-", "") if published_element is not None and published_element.text else ""

            authors = []
            for author in entry.findall("atom:author", namespace):
                name_element = author.find("atom:name", namespace)
                if name_element is not None and name_element.text:
                    authors.append(name_element.text.strip())

            papers.append(PaperMetadata(
                arxiv_id=arxiv_id,
                title=title,
                abstract=abstract,
                published_date=published_date,
                authors=authors
            ))

        return papers


class SemanticScholarAdapter:
    def __init__(self, client: httpx.AsyncClient, api_key: Optional[str] = None):
        self.client = client
        self.headers = {"x-api-key": api_key} if api_key else {}
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/arXiv:"

    async def get_citations(self, arxiv_id: str) -> List[str]:
        url = f"{self.base_url}{arxiv_id}?fields=citations"
        response = await self.client.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return [
            item["arxivId"] for item in data.get("citations", [])
            if item.get("arxivId") is not None
        ]
