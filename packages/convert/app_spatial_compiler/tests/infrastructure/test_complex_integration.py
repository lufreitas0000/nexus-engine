import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_resolves_complex_table_with_math_and_accents() -> None:
    payload = [
        {"char": "P", "x0": 10.0, "y0": 10.0, "x1": 15.0, "y1": 15.0},
        {"char": "a", "x0": 16.0, "y0": 10.0, "x1": 20.0, "y1": 15.0},
        {"char": "r", "x0": 21.0, "y0": 10.0, "x1": 25.0, "y1": 15.0},
        {"char": "â", "x0": 26.0, "y0": 10.0, "x1": 30.0, "y1": 15.0},
        {"char": "m", "x0": 31.0, "y0": 10.0, "x1": 35.0, "y1": 15.0},
        {"char": "e", "x0": 36.0, "y0": 10.0, "x1": 40.0, "y1": 15.0},
        {"char": "t", "x0": 41.0, "y0": 10.0, "x1": 45.0, "y1": 15.0},
        {"char": "r", "x0": 46.0, "y0": 10.0, "x1": 50.0, "y1": 15.0},
        {"char": "o", "x0": 51.0, "y0": 10.0, "x1": 55.0, "y1": 15.0},
        {"char": "-", "x0": 10.0, "y0": 20.0, "x1": 100.0, "y1": 21.0},
        {"char": "M", "x0": 10.0, "y0": 30.0, "x1": 15.0, "y1": 35.0},
        {"char": "é", "x0": 16.0, "y0": 30.0, "x1": 20.0, "y1": 35.0},
        {"char": "t", "x0": 21.0, "y0": 30.0, "x1": 25.0, "y1": 35.0},
        {"char": "R", "x0": 60.0, "y0": 30.0, "x1": 70.0, "y1": 40.0},
        {"char": "μ", "x0": 71.0, "y0": 38.0, "x1": 75.0, "y1": 42.0},
        {"char": "ν", "x0": 71.0, "y0": 28.0, "x1": 75.0, "y1": 32.0}
    ]
    result = runner.invoke(app, [json.dumps(payload)])
    assert result.exit_code == 0
    assert "Parâmetro" in result.stdout
    # Symbols μ and ν must be converted to LaTeX equivalents
    assert "$$R^{\\nu}_{\\mu}$$" in result.stdout
