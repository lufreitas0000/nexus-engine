from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Block(BaseModel):
    id: str
    block_type: str
    content: Optional[str] = ""

class Page(BaseModel):
    page_number: Optional[int] = None
    blocks: List[Block] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pages: List[Page] = Field(default_factory=list)
