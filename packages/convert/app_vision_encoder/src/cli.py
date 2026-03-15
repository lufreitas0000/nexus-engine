"""
Command Line Interface (CLI) Adapter for the Vision Encoder.
Provides the primary driving port for injecting dependencies and executing the spatial-to-semantic mapping.
"""

import os
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from src.services.encoder_service import generate_semantic_ast_node
from src.domain.ports import VisionEncoderPort

app = typer.Typer(help="Vision Encoder: Map continuous physical image tensors to discrete semantic AST nodes.")
console = Console()

@app.command()
def encode(
    image_path: Path = typer.Argument(..., help="Path to the physical image tensor."),
    use_fake: bool = typer.Option(False, "--use-fake", help="Bypass VLM inference, use deterministic Fake adapter."),
    use_api: bool = typer.Option(False, "--use-api", help="Delegate inference to external HTTP API.")
) -> None:
    """Executes the semantic encoding pipeline on a target physical image tensor."""
    console.print(Panel(f"Target Tensor: [cyan]{image_path}[/cyan]", title="Vision Encoder Engine"))

    if not image_path.exists():
        console.print(f"[bold red]Fatal Error:[/bold red] Tensor artifact not found at {image_path}")
        raise typer.Exit(code=1)

    encoder: VisionEncoderPort
    if use_fake:
        console.print("[yellow]Notice: Injecting deterministic FakeVisionEncoderAdapter.[/yellow]")
        from tests.conftest import FakeVisionEncoderAdapter
        encoder = FakeVisionEncoderAdapter()
    elif use_api:
        console.print("[yellow]Notice: Injecting ExternalAPIAdapter (HTTP Socket Delegation).[/yellow]")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            console.print("[bold red]Fatal Error:[/bold red] OPENAI_API_KEY environment variable undefined.")
            raise typer.Exit(code=1)
        
        from src.adapters.external_api import ExternalAPIAdapter
        encoder = ExternalAPIAdapter(api_key=api_key)
    else:
        console.print("[green]Notice: Injecting LocalQuantizedAdapter (4-bit VRAM Allocation).[/green]")
        console.print("[dim]Lazy-loading PyTorch/Transformers context...[/dim]")
        from src.adapters.local_quantized import LocalQuantizedAdapter
        encoder = LocalQuantizedAdapter()

    try:
        console.print(r"[dim]Executing mapping f: R^{H x W x C} -> \Sigma^* ...[/dim]")
        ast_node = generate_semantic_ast_node(image_path=image_path, encoder=encoder)
        
        console.print(r"\n[bold green]Discrete \Sigma^* Output:[/bold green]")
        console.print(ast_node.content)
        console.print(f"\n[dim]Metadata Trace: {ast_node.metadata}[/dim]")
    except Exception as e:
        console.print(f"\n[bold red]Execution Failure:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
