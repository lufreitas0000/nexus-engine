import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Document, Section, Paragraph, Metadata
from pydantic import ValidationError

def test_document_serialization():
    doc = Document(
        metadata=Metadata(title="Test Doc"),
        sections=[
            Section(
                title="Intro",
                content=[Paragraph(text="Hello world")]
            )
        ]
    )
    
    dump = doc.model_dump()
    assert dump["metadata"]["title"] == "Test Doc"
    assert len(dump["sections"]) == 1
    assert dump["sections"][0]["title"] == "Intro"
    assert dump["sections"][0]["content"][0]["text"] == "Hello world"
    
    # Test deserialization
    new_doc = Document.model_validate(dump)
    assert new_doc.metadata.title == "Test Doc"
    assert new_doc.sections[0].content[0].text == "Hello world"

def test_invalid_schema():
    with pytest.raises(ValidationError):
        # Paragraph requires text
        Paragraph(text=None)

    with pytest.raises(ValidationError):
        # content must be a list of paragraphs
        Section(content=["just a string"])
