import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def build_line(text: str, x: float, y: float, size: float = 12.0) -> list[dict]:
    nodes = []
    curr_x = x
    for c in text:
        nodes.append({"char": c, "x0": curr_x, "y0": y, "x1": curr_x + size*0.5, "y1": y + size, "font_size": size})
        curr_x += size*0.5 + 1.0
    return nodes

def test_integrated_academic_document() -> None:
    manifold = []
    
    # Page 1: Margin content (Header) and Title
    manifold += build_line("COPYRIGHT 2026 - IGNORE ME", 100, 20, size=8.0) # Should be filtered
    manifold += build_line("1. Theoretical Foundation", 50, 100, size=18.0)
    manifold += build_line(r"The mapping $f: \mathbb{R}^2 \to \text{AST}$ is discrete.", 50, 150)
    
    # Page 2: Two-Column Text (Corrected X-spacing) and Einstein
    manifold += build_line("Column Left: Segment A.", 50, 1100)
    manifold += build_line("Column Right: Segment B.", 400, 1100) # Increased X to 400
    
    # Einstein: E = mc^2
    manifold += [
        {"char": "E", "x0": 200, "y0": 1300, "x1": 210, "y1": 1315, "font_size": 15.0},
        {"char": "=", "x0": 215, "y0": 1300, "x1": 225, "y1": 1315, "font_size": 15.0},
        {"char": "m", "x0": 230, "y0": 1300, "x1": 240, "y1": 1315, "font_size": 15.0},
        {"char": "c", "x0": 245, "y0": 1300, "x1": 255, "y1": 1315, "font_size": 15.0},
        {"char": "2", "x0": 256, "y0": 1292, "x1": 262, "y1": 1298, "font_size": 10.0}
    ]

    result = runner.invoke(app, [json.dumps(manifold)])
    
    assert result.exit_code == 0
    # Assert header was ignored
    assert "COPYRIGHT" not in result.stdout
    # Assert structural survival
    assert "Theoretical Foundation" in result.stdout
    assert "Column Left" in result.stdout
    assert "Column Right" in result.stdout
    # Assert math resolution with Markdown wrapping
    assert "$$E=mc^{2}$$" in result.stdout.replace(" ", "")
