import json
from typer.testing import CliRunner
from app_spatial_compiler.src.infrastructure.cli import app

runner = CliRunner()

def test_cli_wires_di_container_and_executes_compilation() -> None:
    """
    Asserts the Primary Driving Adapter correctly instantiates the continuous 
    memory structures from a discrete JSON input, wires the pure domain morphisms, 
    and flushes the Markdown AST to stdout.
    """
    # Define a minimal 2D manifold serialized as a JSON string
    synthetic_payload = [
        {"char": "E", "x0": 10.0, "y0": 10.0, "x1": 15.0, "y1": 15.0},
        {"char": "=", "x0": 16.0, "y0": 10.0, "x1": 20.0, "y1": 15.0},
        {"char": "m", "x0": 21.0, "y0": 10.0, "x1": 25.0, "y1": 15.0},
        {"char": "c", "x0": 26.0, "y0": 10.0, "x1": 30.0, "y1": 15.0},
        {"char": "2", "x0": 31.0, "y0": 5.0,  "x1": 35.0, "y1": 9.0}  # Elevated superscript
    ]
    
    input_str = json.dumps(synthetic_payload)
    
    # Execute the CLI morphism
    result = runner.invoke(app, ["compile", input_str])
    
    # Assert successful process termination
    assert result.exit_code == 0
    
    # The pure graph grammar must resolve the elevation to a LaTeX superscript
    assert "E=mc^{2}" in result.stdout
