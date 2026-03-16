import json
import sys
from typing import Annotated, Optional
from collections.abc import Sequence

import typer
from rich.console import Console

from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.services.topology import GeometricParser
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver
from app_spatial_compiler.src.domain.geometry.tessellation import detect_graphical_voids
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase
from app_spatial_compiler.src.infrastructure.adapters.vision_encoder import VisionEncoderAdapter

app = typer.Typer(help="Spatial Compiler: Maps continuous 2D Euclidean manifolds to 1D ASTs.")
error_console = Console(stderr=True)

class CompositeSpatialCompiler:
    def __init__(self) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()
        self.vision_adapter = VisionEncoderAdapter()

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        # 1. Detect and resolve graphical voids (Figures)
        # Assuming standard A4 bounds for the deduction manifold
        voids = detect_graphical_voids(nodes, (0.0, 0.0, 595.0, 842.0))
        resolved_figures = [self.vision_adapter.resolve_subgraph(v) for v in voids]
        
        # 2. Resolve Mathematical and Textual topologies
        content = self.math_resolver.resolve_manifold(nodes)
        if not content:
            ast = self.geometric_parser.compile_graph(nodes)
            content = ast.content
            
        full_content = "\n\n".join(resolved_figures + [content])
        return MarkdownAST(content=full_content, metadata={"figures_detected": str(len(voids))})

@app.command()
def compile(
    payload: Annotated[Optional[str], typer.Argument(help="JSON serialized manifold string")] = None,
    file: Annotated[Optional[typer.FileText], typer.Option("--file", "-f", help="Path to JSON manifold file")] = None
) -> None:
    input_data: str = ""
    if payload:
        input_data = payload
    elif file:
        input_data = file.read()
    elif not sys.stdin.isatty():
        input_data = sys.stdin.read()
    else:
        error_console.print("[bold red]Error:[/bold red] No input provided.")
        raise typer.Exit(code=1)

    try:
        raw_nodes = json.loads(input_data)
        manifold = [SpatialNode(char=n["char"], x0=n["x0"], y0=n["y0"], x1=n["x1"], y1=n["y1"]) for n in raw_nodes]
    except Exception as e:
        error_console.print(f"[bold red]Fault:[/bold red] {e}")
        raise typer.Exit(code=1)

    port = CompositeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)
    ast = use_case.execute(manifold)
    
    error_console.print(f"[bold cyan]Metadata:[/bold cyan] {ast.metadata}")
    sys.stdout.write(ast.content + "\n")
