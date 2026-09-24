from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ConvertedDocument:
    arxiv_id: str
    ast_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
