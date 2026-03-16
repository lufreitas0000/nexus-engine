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
from app_spatial_compiler.src.infrastructure.adapters.pdf_extractor import PDFExtractorAdapter

app = typer.Typer(help="Spatial Compiler: Maps 2D manifolds to 1D ASTs.")
error_console = Console(stderr=True)

class CompositeSpatialCompiler:
    def __init__(self, ignore_margins: bool = True) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()
        self.vision_adapter = VisionEncoderAdapter()
        self.ignore_margins = ignore_margins

    def is_math_block(self, content: str) -> bool:
        # Avoid greedy math wrapping for standard LaTeX accents
        accents = r"\\[\^'\"~=.]"
        math_signals = r"[\^_{}]|\\(frac|int|mu|nu|alpha|beta|Sigma|partial|mathbb|text)"
        cleaned = re.sub(accents, "", content)
        return bool(re.search(math_signals, cleaned)) or "=" in content

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        # Margin Filter: Ignore content outside the 50pt-792pt vertical band (A4)
        if self.ignore_margins:
            nodes = [n for n in nodes if 50 < (n.y0 % 842) < 792]

        if not nodes:
            # If no nodes survive filtering, check for graphical voids
            voids = detect_graphical_voids([], (0.0, 0.0, 595.0, 842.0))
            resolved = [self.vision_adapter.resolve_subgraph(v) for v in voids]
            return MarkdownAST(content="\n\n".join(resolved), metadata={"status": "void"})

        blocks = get_spatial_blocks(nodes, min_dx=10.0, min_dy=5.0)
        results = []
        for block in blocks:
            math_candidate = self.math_resolver.resolve_manifold(block)
            if self.is_math_block(math_candidate):
                results.append(f"$${math_candidate}$$")
            else:
                ast = self.geometric_parser.compile_graph(block)
                results.append(ast.content)

        return MarkdownAST(content="\n\n".join(results), metadata={"blocks": str(len(blocks))})

@app.command()
def compile(
    payload: Annotated[Optional[str], typer.Argument(help="JSON manifold")] = None,
    pdf: Annotated[Optional[str], typer.Option("--pdf", help="Path to PDF file")] = None
) -> None:
    manifold = []
    if pdf:
        extractor = PDFExtractorAdapter()
        manifold = extractor.extract_nodes(pdf)
    elif payload:
        manifold = [SpatialNode(**n) for n in json.loads(payload)]
    else:
        raise typer.Exit(code=1)

    port = CompositeSpatialCompiler()
    use_case = CompileDocumentUseCase(spatial_compiler=port)
    ast = use_case.execute(manifold)
    sys.stdout.write(ast.content + "\n")

if __name__ == "__main__":
    app()
