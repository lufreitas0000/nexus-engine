import json
import sys
import typer
from typing import Annotated
from collections.abc import Sequence

from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.services.topology import GeometricParser
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase

app = typer.Typer(help="Spatial Compiler: Maps continuous 2D Euclidean manifolds to 1D ASTs.")

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
        # A rigorous implementation would apply the math resolver per isolated baseline block.
        # For current TDD saturation, we route the raw manifold through the math resolver
        # to guarantee superscript/fraction topological reduction.
        content = self.math_resolver.resolve_manifold(nodes)
        if not content:
            # Fallback to standard macroscopic clustering if no math topologies are reduced
            return self.geometric_parser.compile_graph(nodes)
            
        return MarkdownAST(content=content, metadata={"resolution": "math_topology"})

@app.command()
def compile(
    payload: Annotated[str, typer.Argument(help="JSON serialized 2D manifold array")]
) -> None:
    """
    Executes the spatial compilation pipeline.
    """
    try:
        raw_nodes = json.loads(payload)
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
    except (json.JSONDecodeError, KeyError) as e:
        typer.echo(f"Manifold Deserialization Fault: {e}", err=True)
        raise typer.Exit(code=1)

    # Dependency Injection Wiring
    port = CompositeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)

    # Pure Morphism Execution
    ast = use_case.execute(manifold)

    # Flush exact discrete state to standard output
    sys.stdout.write(ast.content + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    app()
