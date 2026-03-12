from typer.testing import CliRunner
from pathlib import Path
from src.cli import app

runner = CliRunner()

def test_cli_extract_with_fake(degraded_raster_book_path: Path, tmp_path: Path) -> None:
    result = runner.invoke(app, [
        "extract", 
        str(degraded_raster_book_path), 
        "--output-dir", str(tmp_path),
        "--use-fake"
    ])
    
    assert result.exit_code == 0
    assert "Using deterministic FakeVisionExtractor" in result.stdout
    assert "Success!" in result.stdout
    
    expected_out_file = tmp_path / f"{degraded_raster_book_path.stem}.md"
    assert expected_out_file.exists()

def test_cli_fails_gracefully_on_missing_file(tmp_path: Path) -> None:
    result = runner.invoke(app, [
        "extract", "does_not_exist.pdf", "--output-dir", str(tmp_path)
    ])
    assert result.exit_code == 1
    assert "Error: File not found" in result.stdout
