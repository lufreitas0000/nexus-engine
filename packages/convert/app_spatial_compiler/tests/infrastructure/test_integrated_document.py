import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def build_line(text: str, x: float, y: float, size: float = 12.0) -> list[dict]:
    nodes = []
    curr_x = x
    for c in text:
        nodes.append({"char": c, "x0": curr_x, "y0": y, "x1": curr_x + size*0.6, "y1": y + size, "font_size": size})
        curr_x += size*0.6 + 1.0
    return nodes

def test_integrated_academic_document() -> None:
    """
    Validates a multi-page academic manifold:
    P1: Header and Intro.
    P2: 2-Column layout and Display Equation.
    P3: Tables and Itemized Lists.
    """
    manifold = []
    
    # Page 1: Abstract and Title (y: 0-1000)
    manifold += build_line("Journal of Computational Geometry", 100, 20, size=10.0)
    manifold += build_line("1. Theoretical Foundation", 50, 100, size=18.0)
    manifold += build_line("The document mapping $f: \mathbb{R}^2 \to \text{AST}$ is discrete.", 50, 150)
    
    # Page 2: Two-Column Text and Einstein (y: 1000-2000)
    manifold += build_line("Column Left: High density text segment.", 50, 1100)
    manifold += build_line("Column Right: Parallel structural block.", 350, 1100)
    # Einstein: E = mc^2
    manifold += [
        {"char": "E", "x0": 200, "y0": 1300, "x1": 210, "y1": 1315, "font_size": 15.0},
        {"char": "=", "x0": 215, "y0": 1300, "x1": 225, "y1": 1315, "font_size": 15.0},
        {"char": "m", "x0": 230, "y0": 1300, "x1": 240, "y1": 1315, "font_size": 15.0},
        {"char": "c", "x0": 245, "y0": 1300, "x1": 255, "y1": 1315, "font_size": 15.0},
        {"char": "2", "x0": 256, "y0": 1290, "x1": 262, "y1": 1298, "font_size": 10.0}
    ]

    # Page 3: Tables (y: 2000-3000)
    manifold += build_line("Table 1: Metric Results", 50, 2100)
    manifold += build_line("Metric", 60, 2200)
    manifold += build_line("Value", 150, 2200)
    manifold += [{"char": "-", "x0": 50, "y0": 2215, "x1": 200, "y1": 2216, "font_size": 12.0}]
    manifold += build_line("F1", 60, 2230)
    manifold += build_line("0.98", 150, 2230)

    result = runner.invoke(app, [json.dumps(manifold)])
    
    assert result.exit_code == 0
    assert "Theoretical Foundation" in result.stdout
    assert "Column Left" in result.stdout
    assert "Column Right" in result.stdout
    # Pylatexenc wraps math symbols in ensuremath or similar commands
    assert "E=mc^{2}" in result.stdout.replace(" ", "")
    assert "Metric" in result.stdout
