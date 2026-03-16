import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_wires_di_container_and_executes_compilation() -> None:
    synthetic_payload = [
        {"char": "E", "x0": 10.0, "y0": 10.0, "x1": 15.0, "y1": 15.0},
        {"char": "=", "x0": 16.0, "y0": 10.0, "x1": 20.0, "y1": 15.0},
        {"char": "m", "x0": 21.0, "y0": 10.0, "x1": 25.0, "y1": 15.0},
        {"char": "c", "x0": 26.0, "y0": 10.0, "x1": 30.0, "y1": 15.0},
        {"char": "2", "x0": 31.0, "y0": 5.0,  "x1": 35.0, "y1": 9.0}
    ]
    result = runner.invoke(app, [json.dumps(synthetic_payload)])
    assert result.exit_code == 0
    # Proximity invariant must prevent E^{2} and resolve E=mc^{2}
    assert "$$E=mc^{2}$$" in result.stdout
