import json
import sys
import statistics
from typing import Annotated, Optional
from collections.abc import Sequence

import typer
from rich.console import Console

from app_spatial_compiler.src.domain.models import SpatialNode, MarkdownAST, BlockType
from app_spatial_compiler.src.domain.services.topology import GeometricParser
from app_spatial_compiler.src.domain.services.math_topology import MathTopologyResolver
from app_spatial_compiler.src.domain.geometry.tessellation import detect_graphical_voids, get_spatial_blocks
from app_spatial_compiler.src.application.use_cases.compile_document import CompileDocumentUseCase
from app_spatial_compiler.src.infrastructure.adapters.vision_encoder import VisionEncoderAdapter
from app_spatial_compiler.src.infrastructure.adapters.pdf_extractor import PDFExtractorAdapter
from app_spatial_compiler.src.domain.services.classifier import BlockClassifier

app = typer.Typer(help="Spatial Compiler: Maps 2D manifolds to 1D ASTs.")
error_console = Console(stderr=True)

class CompositeSpatialCompiler:
    def __init__(self, ignore_margins: bool = True) -> None:
        self.geometric_parser = GeometricParser()
        self.math_resolver = MathTopologyResolver()
        self.vision_adapter = VisionEncoderAdapter()
        self.ignore_margins = ignore_margins

    def compile_graph(self, nodes: Sequence[SpatialNode]) -> MarkdownAST:
        if not nodes: return MarkdownAST(content="", metadata={})
        page_median_h = statistics.median(n.font_size if n.font_size else n.height for n in nodes)

        if self.ignore_margins:
            nodes = [n for n in nodes if 50 < (n.y0 % 842) < 792]

        blocks = get_spatial_blocks(nodes, min_dx=10.0, min_dy=5.0)
        classifier = BlockClassifier()
        results = []

        for block in blocks:
            b_type, level = classifier.classify(block, page_median_h)

            if b_type == BlockType.MATH:
                math_str = self.math_resolver.resolve_manifold(block)
                results.append(f"$${math_str}$$")
            elif b_type == BlockType.HEADER:
                text_ast = self.geometric_parser.compile_graph(block)
                prefix = "#" * level
                results.append(f"{prefix} {text_ast.content}")
            else:
                text_ast = self.geometric_parser.compile_graph(block)
                results.append(text_ast.content)

        return MarkdownAST(content="\n\n".join(results), metadata={"blocks": str(len(blocks))})

@app.command()
def compile(
    payload: Annotated[Optional[str], typer.Argument(help="JSON manifold")] = None,
    pdf: Annotated[Optional[str], typer.Option("--pdf", help="Path to PDF file")] = None
) -> None:
    manifold: list[SpatialNode] = []
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
