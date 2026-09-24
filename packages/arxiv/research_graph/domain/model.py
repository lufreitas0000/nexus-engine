from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PaperMetadata:
    arxiv_id: str
    title: str
    abstract: str
    published_date: str  # Format: YYYYMMDD
    authors: List[str]
