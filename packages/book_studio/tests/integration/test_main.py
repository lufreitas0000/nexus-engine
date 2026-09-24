import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from book_studio.main import cli
from book_studio.core.schemas import ExtractionResult, Page, Block

def test_run_pipeline_skip_ocr(mocker, tmp_path):
    """Tests the state-machine execution bypassing the heavy OCR layer."""
    runner = CliRunner()
    
    book_dir = tmp_path / "test_book"
    book_dir.mkdir(parents=True, exist_ok=True)

    book_yaml = book_dir / "book.yaml"
    book_yaml.write_text("book_id: test_book\ntitle: Test Book\n", encoding="utf-8")

    for d in ["00_raw", "01_segmented", "02_stitched", "03_verified_md", "04_final_tex", "05_figures/raw", "06_compiled"]:
        (book_dir / d).mkdir(parents=True, exist_ok=True)
        
    mocker.patch("book_studio.main.dvc_track")  

    pdf_path = book_dir / "00_raw" / "test_book.pdf"
    pdf_path.touch()

    state_segmented = book_dir / "01_segmented" / "test_book.json"
    
    # Corrected Block Schema: Header and body text separated into distinct blocks
    mock_data = ExtractionResult(
        pages=[
            Page(
                page_number=1, 
                blocks=[
                    Block(id="1", block_type="Text", content="1.2 Probability Density"),
                    Block(id="2", block_type="Text", content="The wave function")
                ]
            )
        ]
    )
    with open(state_segmented, "w", encoding="utf-8") as f:
        json.dump(mock_data.model_dump(), f)

    result = runner.invoke(cli, ["run-pipeline", str(book_yaml), "--skip-ocr"])
    
    assert result.exit_code == 0
    assert "[Stage 1] Skipped — loading from:" in result.output
    assert "[Stage 4] Assembling LaTeX chunks" in result.output
    
    md_file = book_dir / "03_verified_md" / "01_02_Probability_Density.md"
    tex_file = book_dir / "04_final_tex" / "01_02_Probability_Density.tex"
    
    assert md_file.exists()
    assert tex_file.exists()
