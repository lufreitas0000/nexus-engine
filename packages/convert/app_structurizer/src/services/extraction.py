"""
Application Service orchestrating the topological routing and AST generation.
"""

from pathlib import Path
import fitz  # type: ignore
from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor, SpatialCompiler, SpatialNode
from src.domain.services.topology import PdfTopologyAnalyzer

def extract_document_to_markdown(
    file_path: Path,
    topology_analyzer: PdfTopologyAnalyzer,
    vision_extractor: VisionExtractor,
    spatial_compiler: SpatialCompiler,
    output_dir: str = "./output"
) -> Path:
    """
    Deterministically routes the document extraction based on its physical memory layout.
    """
    doc = RawDocument(file_path=file_path, file_size_bytes=file_path.stat().st_size)
    q_factor = topology_analyzer.analyze(doc)
    
    ast: MarkdownAST
    
    # Threshold for mathematical topology validity
    if q_factor >= 0.95:
        # Extract the O(N) spatial graph in RAM
        nodes = _extract_spatial_graph(doc)
        # Dispatch to the graph compiler
        ast = spatial_compiler.compile_graph(nodes)
    else:
        # Fallback to dense tensor OCR inference
        ast = vision_extractor.extract_ast(doc)
        
    out_path = Path(output_dir) / f"{file_path.stem}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ast.content, encoding="utf-8")
    
    return out_path

def _extract_spatial_graph(document: RawDocument) -> list[SpatialNode]:
    """
    Extracts the continuous vector boundaries into discrete spatial nodes.
    """
    nodes = []
    pdf = fitz.open(str(document.file_path))
    try:
        for page in pdf:
            # get_text("words") returns (x0, y0, x1, y1, word, block_no, line_no, word_no)
            words = page.get_text("words")
            for w in words:
                nodes.append(SpatialNode(char=w[4], x0=w[0], y0=w[1], x1=w[2], y1=w[3]))
    finally:
        pdf.close()
    return nodes
