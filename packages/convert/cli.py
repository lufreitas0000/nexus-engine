import typer
from pathlib import Path

from app_orchestrator.pipeline import PipelineOrchestrator

app = typer.Typer(help="Semantic PDF Pipeline CLI")

# Dummy adapter functions wrapping the logic of the underlying modules
# As per phase 5 scope, these just demonstrate the public interface consumption.


def dummy_extractor_adapter(pdf_path: Path) -> str:
    """Mock adapter for app_structurizer / PDF router"""
    typer.echo(f"  [Extractor] Extracting manifold from {pdf_path}...")
    return f"manifold_data_for_{pdf_path.name}"


def dummy_spatial_adapter(manifold_data: str) -> str:
    """Mock adapter for app_spatial_compiler"""
    typer.echo("  [Spatial] Compiling spatial AST...")
    return f"spatial_ast_with_placeholders_from({manifold_data})"


def dummy_vision_adapter(spatial_ast: str) -> str:
    """Mock adapter for app_vision_encoder"""
    typer.echo("  [Vision] Resolving final semantic AST...")
    return f"final_resolved_ast_from({spatial_ast})"


@app.command()
def convert(pdf_path: Path) -> None:
    """
    Convert a PDF into a structured Markdown AST using the Pipeline Orchestrator.
    """
    typer.echo(f"Initializing conversion pipeline for: {pdf_path}")

    orchestrator = PipelineOrchestrator(
        extractor_fn=dummy_extractor_adapter,
        spatial_fn=dummy_spatial_adapter,
        vision_fn=dummy_vision_adapter,
    )

    try:
        final_ast = orchestrator.process(pdf_path)
        typer.echo("\nConversion Successful. Final AST Output:")
        typer.echo(final_ast)
    except Exception as e:
        typer.echo(f"Pipeline failed: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
