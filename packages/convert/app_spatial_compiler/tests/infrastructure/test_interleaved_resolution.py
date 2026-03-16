import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_resolves_interleaved_text_and_math() -> None:
    """
    Asserts that a manifold with a text paragraph followed by a 
    mathematical expression is resolved without the math logic 
    consuming the text block.
    """
    payload = [
        # Paragraph: "Hi"
        {"char": "H", "x0": 10.0, "y0": 10.0, "x1": 12.0, "y1": 15.0},
        {"char": "i", "x0": 12.0, "y0": 10.0, "x1": 13.0, "y1": 15.0},
        
        # Gap for XY-Cut to detect new block
        
        # Math: "E=mc^2" (Distant Y-axis)
        {"char": "E", "x0": 10.0, "y0": 50.0, "x1": 15.0, "y1": 55.0},
        {"char": "=", "x0": 16.0, "y0": 50.0, "x1": 20.0, "y1": 55.0},
        {"char": "m", "x0": 21.0, "y0": 50.0, "x1": 25.0, "y1": 55.0},
        {"char": "c", "x0": 26.0, "y0": 50.0, "x1": 30.0, "y1": 55.0},
        {"char": "2", "x0": 31.0, "y0": 45.0, "x1": 35.0, "y1": 49.0}
    ]
    
    result = runner.invoke(app, [json.dumps(payload)])
    
    assert result.exit_code == 0
    # Both blocks must survive the reduction
    assert "Hi" in result.stdout
    assert "E=mc^{2}" in result.stdout
