from pydantic import BaseModel, Field
from typing import List, Optional

class Metadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    # Flexible container for any extra data
    extra: dict = Field(default_factory=dict)

class Paragraph(BaseModel):
    text: str

class Section(BaseModel):
    title: Optional[str] = None
    content: List[Paragraph] = Field(default_factory=list)

class Document(BaseModel):
    metadata: Metadata = Field(default_factory=Metadata)
    sections: List[Section] = Field(default_factory=list)
