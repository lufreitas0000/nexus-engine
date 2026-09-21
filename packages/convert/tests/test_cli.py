from typer.testing import CliRunner
from cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "convert" in result.stdout

def test_convert_command_exists():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "Convert a PDF" in result.stdout
