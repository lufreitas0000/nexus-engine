import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def make_text(text: str, x: float, y: float, size: float = 12.0) -> list[dict]:
    nodes = []
    curr_x = x
    for c in text:
        nodes.append({"char": c, "x0": curr_x, "y0": y, "x1": curr_x + size*0.6, "y1": y + size})
        curr_x += size*0.6 + 1.0
    return nodes

def test_integrated_academic_document() -> None:
    """
    Simulates a 3-page academic document with disparate typographic blocks.
    Page 1: Header, Section, Paragraph.
    Page 2: 2-Column Text and Display Equation (Einstein).
    Page 3: Itemize and Table.
    """
    manifold = []
    
    # Page 1: Introduction (y: 0 - 800)
    manifold += make_text("Header: Journal of Physics", 100, 20, size=8.0)
    manifold += make_text("1. Introduction", 50, 100, size=16.0)
    manifold += make_text("This is a standard LaTeX paragraph with accents: áéíóú.", 50, 150)
    
    # Page 2: Math and Columns (y: 1000 - 1800)
    # Left Column
    manifold += make_text("Col A: High density text.", 50, 1100)
    # Right Column
    manifold += make_text("Col B: Parallel block.", 350, 1100)
    # Display Equation
    manifold += [{"char": "E", "x0": 200, "y0": 1300, "x1": 210, "y1": 1315},
                 {"char": "=", "x0": 215, "y0": 1300, "x1": 225, "y1": 1315},
                 {"char": "m", "x0": 230, "y0": 1300, "x1": 240, "y1": 1315},
                 {"char": "c", "x0": 245, "y0": 1300, "x1": 255, "y1": 1315},
                 {"char": "2", "x0": 256, "y0": 1290, "x1": 262, "y1": 1298}]

    # Page 3: List and Table (y: 2000 - 2800)
    manifold += make_text("• Item 1", 50, 2100)
    # Table Grid Reconstruction
    manifold += make_text("ID", 60, 2300)
    manifold += make_text("Val", 150, 2300)
    manifold += [{"char": "-", "x0": 50, "y0": 2315, "x1": 200, "y1": 2316}] # Table line
    manifold += make_text("01", 60, 2330)
    manifold += make_text("100", 150, 2330)

    result = runner.invoke(app, [json.dumps(manifold)])
    
    assert result.exit_code == 0
    # Assert structural survival
    assert "1. Introduction" in result.stdout
    assert "áéíóú" in result.stdout
    # Assert math resolution
    assert "$$E=mc^{2}$$" in result.stdout
    # Assert column isolation
    assert "Col A" in result.stdout
    assert "Col B" in result.stdout
