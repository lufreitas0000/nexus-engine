import json
import sys
import re
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
    def __init__(self, ignore_margins: bool = True) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()
        self.vision_adapter = VisionEncoderAdapter()
        self.ignore_margins = ignore_margins

    def is_math_block(self, content: str) -> bool:
        # Avoid greedy math wrapping for standard accents (\^, \', \", \~)
        accents = r"\\[\^'\"~=.]"
        math_signals = r"[\^_{}]|\\(frac|int|mu|nu|alpha|beta|Sigma|partial)"
        
        # Strip accents before checking for math backslashes
        cleaned = re.sub(accents, "", content)
        return bool(re.search(math_signals, cleaned)) or "=" in content

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        # Filter Ignorable Content (Headers/Footers based on standard margins)
        # Assuming 842pt height; ignore top 50pt and bottom 50pt
        if self.ignore_margins:
            nodes = [n for n in nodes if 50 < (n.y0 % 842) < 792]

        voids = detect_graphical_voids(nodes, (0.0, 0.0, 595.0, 842.0))
        resolved_figures = [self.vision_adapter.resolve_subgraph(v) for v in voids]
        
        blocks = get_spatial_blocks(nodes)
        results = []
        for block in blocks:
            math_candidate = self.math_resolver.resolve_manifold(block)
            if self.is_math_block(math_candidate):
                results.append(f"$${math_candidate}$$")
            else:
                ast = self.geometric_parser.compile_graph(block)
                results.append(ast.content)
            
        full_content = "\n\n".join(resolved_figures + results)
        return MarkdownAST(content=full_content, metadata={"blocks": str(len(blocks))})

@app.command()
def compile(payload: Annotated[Optional[str], typer.Argument()] = None) -> None:
    if not payload: raise typer.Exit(1)
    try:
        manifold = [SpatialNode(**n) for n in json.loads(payload)]
    except Exception as e:
        error_console.print(f"Fault: {e}"); raise typer.Exit(1)

    use_case = CompileDocumentUseCase(spatial_compiler=CompositeSpatialCompiler())
    ast = use_case.execute(manifold)
    sys.stdout.write(ast.content + "\n")
