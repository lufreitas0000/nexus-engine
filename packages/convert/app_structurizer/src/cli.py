"""
Command Line Interface (CLI) Adapter.
Acts as the primary entry point, reading from the terminal, injecting dependencies,
and invoking the Application Service.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from src.services.extraction import extract_document_to_markdown
from src.domain.ports import VisionExtractor

app = typer.Typer(help="Semantic PDF Structurizer: Map continuous PDF tensors to discrete Markdown ASTs.")
console = Console()

def _get_hardware_info() -> str:
    """Probes the local system for hardware accelerators via PyTorch."""
    try:
        import torch # type: ignore
        if torch.cuda.is_available():
            return f"[green]NVIDIA GPU (CUDA) - {torch.cuda.get_device_name(0)}[/green]"
        return "[yellow]CPU (Standard RAM)[/yellow]"
    except ImportError:
        return "[red]Unknown (PyTorch not installed)[/red]"

@app.command()
def extract(
    file_path: Path = typer.Argument(..., help="Path to the binary PDF tensor."),
    output_dir: Path = typer.Option(Path("./output"), "--output-dir", "-o", help="Directory to flush the Markdown AST."),
    use_fake: bool = typer.Option(False, "--use-fake", help="Bypass ML inference and use the deterministic Fake adapter.")
):
    """Executes the extraction pipeline on a target PDF."""
    console.print(Panel(f"Target: [cyan]{file_path}[/cyan]\nOutput: [cyan]{output_dir}[/cyan]", title="Structurizer Engine"))
    
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found at {file_path}")
        raise typer.Exit(code=1)

    extractor: VisionExtractor
    if use_fake:
        console.print("[yellow]Warning: Using deterministic FakeVisionExtractor. Bypassing PyTorch.[/yellow]")
        from tests.conftest import FakeVisionExtractor
        extractor = FakeVisionExtractor()
    else:
        hardware = _get_hardware_info()
        console.print(f"Hardware Probed: {hardware}")
        console.print("[dim]Lazy-loading PyTorch weights into memory...[/dim]")
        
        from src.adapters.marker_adapter import MarkerVisionAdapter
        extractor = MarkerVisionAdapter()
        console.print("[green]ML Adapters Loaded.[/green]")

    try:
        console.print("[dim]Initiating mathematical mapping (Continuous -> Discrete)...[/dim]")
        out_file = extract_document_to_markdown(file_path, extractor, output_dir)
        console.print(f"\n[bold green]Success![/bold green] AST flushed to: [cyan]{out_file}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
