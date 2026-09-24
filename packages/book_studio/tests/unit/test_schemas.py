import pytest
from nexus_schema import Document, Section, Paragraph, Metadata
from book_studio.core.schemas import ExtractionResult, Page, Block
from book_studio.core.assembler import Assembler
from pathlib import Path

def test_extraction_result_to_and_from_nexus_document():
    raw = ExtractionResult(
        metadata={"title": "Quantum Mechanics", "author": "Gordon Baym"},
        pages=[
            Page(
                page_number=1,
                blocks=[
                    Block(id="1", block_type="SectionHeader", content="Chapter 1"),
                    Block(id="2", block_type="Text", content="Introduction to quantum theory.")
                ]
            )
        ]
    )

    doc = raw.to_nexus_document()
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Quantum Mechanics"
    assert doc.metadata.author == "Gordon Baym"
    assert len(doc.sections) == 1
    assert len(doc.sections[0].content) == 2
    assert doc.sections[0].content[0].text == "Chapter 1"
    assert doc.sections[0].content[1].text == "Introduction to quantum theory."

    restored = ExtractionResult.from_nexus_document(doc)
    assert isinstance(restored, ExtractionResult)
    assert restored.metadata["title"] == "Quantum Mechanics"
    assert restored.metadata["author"] == "Gordon Baym"
    assert len(restored.pages) == 1
    assert len(restored.pages[0].blocks) == 2
    assert restored.pages[0].blocks[0].content == "Chapter 1"
    assert restored.pages[0].blocks[1].content == "Introduction to quantum theory."

def test_assembler_to_nexus_document(tmp_path):
    output_md = tmp_path / "md"
    output_tex = tmp_path / "tex"
    assembler = Assembler(output_md, output_tex)

    raw = ExtractionResult(
        pages=[
            Page(
                page_number=1,
                blocks=[
                    Block(id="1", block_type="Text", content="Chapter 1 The Schrodinger Equation"),
                    Block(id="2", block_type="Text", content="Some text here."),
                    Block(id="3", block_type="Text", content="1.2 Probability Density"),
                    Block(id="4", block_type="Text", content="More text here.")
                ]
            )
        ]
    )

    doc = assembler.to_nexus_document(raw)
    assert isinstance(doc, Document)
    assert len(doc.sections) == 2
    assert doc.sections[0].title == "The Schrodinger Equation"
    assert doc.sections[0].content[0].text == "Some text here."
    assert doc.sections[1].title == "Probability Density"
    assert doc.sections[1].content[0].text == "More text here."
