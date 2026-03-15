"""
Validation suite for the Command Line Interface (CLI) driving adapter.
"""

from typer.testing import CliRunner
from pathlib import Path
from src.cli import app

runner = CliRunner()

def test_cli_encode_with_fake_adapter(synthetic_image_tensor: Path) -> None:
    """
    Validates terminal input parsing, dependency injection of the Fake adapter,
    and the successful flush of the semantic string to stdout in O(1) time.
    """
    result = runner.invoke(app, [
        "encode",
        str(synthetic_image_tensor),
        "--use-fake"
    ])
    
    assert result.exit_code == 0
    assert "Injecting deterministic FakeVisionEncoderAdapter" in result.stdout
    assert "Semantic description of tensor at" in result.stdout
    assert "FakeAdapter" in result.stdout

def test_cli_fails_gracefully_on_missing_tensor() -> None:
    """
    Asserts that the CLI mathematically halts execution if the physical pointer is invalid,
    preventing null states from propagating to the dependency injection layer.
    """
    result = runner.invoke(app, [
        "encode",
        "nonexistent_tensor_artifact.png"
    ])
    
    assert result.exit_code == 1
    assert "Fatal Error: Tensor artifact not found" in result.stdout
