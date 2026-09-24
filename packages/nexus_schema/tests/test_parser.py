from nexus_schema import Document, Section, Paragraph, markdown_to_document

def test_markdown_to_document():
    md = """# Introduction
This is the first paragraph.

This is the second paragraph.

## Background
More text here."""

    doc = markdown_to_document(md)
    assert len(doc.sections) == 2

    assert doc.sections[0].title == "Introduction"
    assert len(doc.sections[0].content) == 2
    assert doc.sections[0].content[0].text == "This is the first paragraph."
    assert doc.sections[0].content[1].text == "This is the second paragraph."

    assert doc.sections[1].title == "Background"
    assert len(doc.sections[1].content) == 1
    assert doc.sections[1].content[0].text == "More text here."

