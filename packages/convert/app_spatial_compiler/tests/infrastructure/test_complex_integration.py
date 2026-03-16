import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_resolves_complex_table_with_math_and_accents() -> None:
    # All Y shifted above 50
    payload = [
        {"char": "P", "x0": 10, "y0": 100, "x1": 15, "y1": 105},
        {"char": "a", "x0": 16, "y0": 100, "x1": 20, "y1": 105},
        {"char": "r", "x0": 21, "y0": 100, "x1": 25, "y1": 105},
        {"char": "â", "x0": 26, "y0": 100, "x1": 30, "y1": 105},
        {"char": "m", "x0": 31, "y0": 100, "x1": 35, "y1": 105},
        {"char": "e", "x0": 36, "y0": 100, "x1": 40, "y1": 105},
        {"char": "t", "x0": 41, "y0": 100, "x1": 45, "y1": 105},
        {"char": "r", "x0": 46, "y0": 100, "x1": 50, "y1": 105},
        {"char": "o", "x0": 51, "y0": 100, "x1": 55, "y1": 105},
        {"char": "-", "x0": 10, "y0": 110, "x1": 60, "y1": 111},
        {"char": "M", "x0": 10, "y0": 120, "x1": 15, "y1": 125},
        {"char": "é", "x0": 16, "y0": 120, "x1": 20, "y1": 125}
    ]
    result = runner.invoke(app, [json.dumps(payload)])
    assert result.exit_code == 0
    # Check for LaTeX-encoded accents
    assert r"Par\^ametro" in result.stdout
    assert r"M\'e" in result.stdout
