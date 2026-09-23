import httpx
import xml.etree.ElementTree as ET
from typing import List, Optional

from research_graph.domain.model import PaperMetadata

class ArxivAdapter:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = "https://export.arxiv.org/api/query"

    async def search_by_query(self, query: str, max_results: int) -> List[PaperMetadata]:
        params = {"search_query": query, "max_results": str(max_results)}
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
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type
)

class RemoteComputeUnavailableError(Exception):
    """Raised when the remote Colab tunnel is permanently unreachable."""
    pass

class ColabComputeAdapter:
    def __init__(self, tunnel_url: str):
        self.tunnel_url = tunnel_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=300.0)

    @retry(
        # Wait 2^x * 1 second between retries, up to 30 seconds
        wait=wait_exponential(multiplier=1, min=2, max=30),
        # Give up after 5 attempts
        stop=stop_after_attempt(5),
        # Only trigger retry on transient network errors
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True # Bubble up the final exception if all retries fail
    )
    async def execute_remote_task(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.tunnel_url}/{endpoint}"

        try:
            response = await self.client.post(url, json=payload)

            # Immediately abort retries and raise custom error for tunnel disconnects
            if response.status_code in (502, 503):
                raise RemoteComputeUnavailableError(
                    f"Colab tunnel disconnected. Status: {response.status_code}"
                )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (502, 503):
                raise RemoteComputeUnavailableError(
                    f"Colab tunnel disconnected. Status: {exc.response.status_code}"
                )
            raise exc
