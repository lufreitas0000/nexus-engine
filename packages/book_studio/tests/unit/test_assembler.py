import pytest
from pathlib import Path
from book_studio.core.schemas import ExtractionResult, Page, Block
from book_studio.core.assembler import SemanticChunker, Assembler

def test_semantic_chunker_regex():
    chunker = SemanticChunker()
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[
                Block(id="1", block_type="Text", content="Chapter 1 The Schrodinger Equation"),
                Block(id="2", block_type="Text", content="Some text here."),
                Block(id="3", block_type="Text", content="1.2 Probability Density"),
                Block(id="4", block_type="Text", content="More text here.")
            ])
        ]
    )
    chunks = chunker.verify_and_chunk(raw)
    
    assert len(chunks) == 2
    assert chunks[0]["filename"] == "01_00_The_Schrodinger_Equation"
    assert chunks[0]["blocks"] == ["Some text here."]
    
    assert chunks[1]["filename"] == "01_02_Probability_Density"
    assert chunks[1]["blocks"] == ["More text here."]
    assert chunks[1]["chapter"] == 1
    assert chunks[1]["section"] == 2

def test_assembler_file_writing(tmp_path):
    output_md = tmp_path / "md"
    output_tex = tmp_path / "tex"
    assembler = Assembler(output_md, output_tex)
    
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[
                Block(id="1", block_type="Text", content="1.2 The Schrodinger Equation"),
                Block(id="2", block_type="Text", content="Let $\\psi$ be the wave function.")
            ])
        ]
    )
    
    assembler.assemble(raw)
    
    expected_md_file = output_md / "01_02_The_Schrodinger_Equation.md"
    expected_tex_file = output_tex / "01_02_The_Schrodinger_Equation.tex"
    
    assert expected_md_file.exists()
    assert expected_tex_file.exists()
    
    md_content = expected_md_file.read_text()
    assert "title: The Schrodinger Equation" in md_content
    assert "status: unverified" in md_content
    assert "Let $\\psi$ be the wave function." in md_content
    
    tex_content = expected_tex_file.read_text()
    assert "\\section{The Schrodinger Equation}" in tex_content
