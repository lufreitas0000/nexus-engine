import json
import sys
from typing import Annotated, Optional
from collections.abc import Sequence

import typer
from rich.console import Console

from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST
from app_spatial_compiler.src.domain.services.topology import GeometricParser
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver
from app_spatial_compiler.src.domain.geometry.tessellation import detect_graphical_voids, get_spatial_blocks
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase
from app_spatial_compiler.src.infrastructure.adapters.vision_encoder import VisionEncoderAdapter

app = typer.Typer(help="Spatial Compiler: Maps 2D manifolds to 1D ASTs.")
error_console = Console(stderr=True)

class CompositeSpatialCompiler:
    def __init__(self) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()
        self.vision_adapter = VisionEncoderAdapter()

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        voids = detect_graphical_voids(nodes, (0.0, 0.0, 595.0, 842.0))
        resolved_figures = [self.vision_adapter.resolve_subgraph(v) for v in voids]
        
        blocks = get_spatial_blocks(nodes)
        results = []
        
        for block in blocks:
            math_candidate = self.math_resolver.resolve_manifold(block)
            # Heuristic: Determine if the block requires LaTeX formatting
            has_operators = any(c in "=-+*/\\^_{}" for n in block for c in n.char)
            is_math = has_operators or "^" in math_candidate or "_" in math_candidate or "\\" in math_candidate
            
            if is_math:
                # Wrap in Markdown display math delimiters
                results.append(f"$${math_candidate}$$")
            else:
                ast = self.geometric_parser.compile_graph(block)
                results.append(ast.content)
            
        full_content = "\n\n".join(resolved_figures + results)
        return MarkdownAST(content=full_content, metadata={"blocks_processed": str(len(blocks))})

@app.command()
def compile(
    payload: Annotated[Optional[str], typer.Argument(help="JSON manifold array")] = None
) -> None:
    if not payload: raise typer.Exit(code=1)
    try:
        raw = json.loads(payload)
        manifold = [SpatialNode(char=n["char"], x0=n["x0"], y0=n["y0"], x1=n["x1"], y1=n["y1"]) for n in raw]
    except Exception as e:
        error_console.print(f"Fault: {e}")
        raise typer.Exit(code=1)

    port = CompositeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)
    ast = use_case.execute(manifold)
    sys.stdout.write(ast.content + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    app()
