import json
import sys
from typing import Annotated, Optional
from collections.abc import Sequence

import typer
from rich.console import Console

from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.services.topology import GeometricParser
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase

app = typer.Typer(help="Spatial Compiler: Maps continuous 2D Euclidean manifolds to 1D ASTs.")
error_console = Console(stderr=True)

class CompositeSpatialCompiler:
    """
    Infrastructure DI composition.
    Satisfies SpatialCompilerPort by orchestrating the macroscopic XY-Cut 
    with the localized O(log N) mathematical graph grammar.
    """
    def __init__(self) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        content = self.math_resolver.resolve_manifold(nodes)
        if not content:
            return self.geometric_parser.compile_graph(nodes)
            
        return MarkdownAST(content=content, metadata={"resolution": "math_topology"})

@app.command()
def compile(
    payload: Annotated[Optional[str], typer.Argument(help="JSON serialized manifold string")] = None,
    file: Annotated[Optional[typer.FileText], typer.Option("--file", "-f", help="Path to JSON manifold file")] = None
) -> None:
    """
    Executes the spatial compilation pipeline. Reads from Argument, --file, or STDIN.
    """
    input_data: str = ""

    # 1. Resolve Input manifold from Argument, File, or STDIN pipe
    if payload:
        input_data = payload
    elif file:
        input_data = file.read()
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read()
    else:
        error_console.print("[bold red]Error:[/bold red] No input manifold provided. Provide a string argument, use --file, or pipe JSON to STDIN.")
        raise typer.Exit(code=1)

    try:
        raw_nodes = json.loads(input_data)
        manifold = [
            SpatialNode(
                char=str(n["char"]),
                x0=float(n["x0"]),
                y0=float(n["y0"]),
                x1=float(n["x1"]),
                y1=float(n["y1"])
            )
            for n in raw_nodes
        ]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        error_console.print(f"[bold red]Manifold Deserialization Fault:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 2. Dependency Injection and Execution
    port = CompositeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)
    ast = use_case.execute(manifold)

    # 3. Telemetry Segregation (stderr)
    error_console.print(f"[bold cyan]Topological Metadata:[/bold cyan] {ast.metadata}")

    # 4. Clean Output (stdout)
    sys.stdout.write(ast.content + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    app()
