import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_resolves_complex_table_with_math_and_accents() -> None:
    payload = [
        # Table Header: "Parâmetro"
        {"char": "P", "x0": 10.0, "y0": 10.0, "x1": 15.0, "y1": 15.0},
        {"char": "a", "x0": 16.0, "y0": 10.0, "x1": 20.0, "y1": 15.0},
        {"char": "r", "x0": 21.0, "y0": 10.0, "x1": 25.0, "y1": 15.0},
        {"char": "â", "x0": 26.0, "y0": 10.0, "x1": 30.0, "y1": 15.0},
        {"char": "m", "x0": 31.0, "y0": 10.0, "x1": 35.0, "y1": 15.0},
        {"char": "e", "x0": 36.0, "y0": 10.0, "x1": 40.0, "y1": 15.0},
        {"char": "t", "x0": 41.0, "y0": 10.0, "x1": 45.0, "y1": 15.0},
        {"char": "r", "x0": 46.0, "y0": 10.0, "x1": 50.0, "y1": 15.0},
        {"char": "o", "x0": 51.0, "y0": 10.0, "x1": 55.0, "y1": 15.0},
        
        # Separator Line
        {"char": "-", "x0": 10.0, "y0": 20.0, "x1": 100.0, "y1": 21.0},
        
        # Row 2 Cell 1: "Métrica"
        {"char": "M", "x0": 10.0, "y0": 30.0, "x1": 15.0, "y1": 35.0},
        {"char": "é", "x0": 16.0, "y0": 30.0, "x1": 20.0, "y1": 35.0},
        {"char": "t", "x0": 21.0, "y0": 30.0, "x1": 25.0, "y1": 35.0},
        {"char": "r", "x0": 26.0, "y0": 30.0, "x1": 30.0, "y1": 35.0},
        {"char": "i", "x0": 31.0, "y0": 30.0, "x1": 32.0, "y1": 35.0},
        {"char": "c", "x0": 33.0, "y0": 30.0, "x1": 37.0, "y1": 35.0},
        {"char": "a", "x0": 38.0, "y0": 30.0, "x1": 42.0, "y1": 35.0},
        
        # Row 2 Cell 2: R_{μ}^{ν} (Tensor with sub and super)
        {"char": "R", "x0": 60.0, "y0": 30.0, "x1": 70.0, "y1": 40.0},
        {"char": "μ", "x0": 71.0, "y0": 38.0, "x1": 75.0, "y1": 42.0}, # Sub
        {"char": "ν", "x0": 71.0, "y0": 28.0, "x1": 75.0, "y1": 32.0}  # Super
    ]
    
    result = runner.invoke(app, [json.dumps(payload)])
    assert result.exit_code == 0
    assert "Parâmetro" in result.stdout
    assert "Métrica" in result.stdout
    assert "R_{μ}^{ν}" in result.stdout
