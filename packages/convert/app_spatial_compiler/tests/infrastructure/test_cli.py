import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_wires_di_container_and_executes_compilation() -> None:
    # Shift Y to 100 to avoid margin filtering
    synthetic_payload = [
        {"char": "E", "x0": 10.0, "y0": 100.0, "x1": 15.0, "y1": 105.0},
        {"char": "=", "x0": 16.0, "y0": 100.0, "x1": 20.0, "y1": 105.0},
        {"char": "m", "x0": 21.0, "y0": 100.0, "x1": 25.0, "y1": 105.0},
        {"char": "c", "x0": 26.0, "y0": 100.0, "x1": 30.0, "y1": 105.0},
        {"char": "2", "x0": 31.0, "y0": 95.0,  "x1": 35.0, "y1": 99.0}
    ]
    result = runner.invoke(app, [json.dumps(synthetic_payload)])
    assert result.exit_code == 0
    assert "$$E=mc^{2}$$" in result.stdout
