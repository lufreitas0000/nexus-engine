"""
Application Service orchestrating the topological routing, AST generation,
and semantic VLM delegation.
"""

from pathlib import Path
import fitz  # type: ignore
from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor, SpatialCompiler, SpatialNode, VisionEncoder
from src.domain.services.topology import PdfTopologyAnalyzer

def extract_document_to_markdown(
    file_path: Path,
    topology_analyzer: PdfTopologyAnalyzer,
    vision_extractor: VisionExtractor,
    spatial_compiler: SpatialCompiler,
    vision_encoder: VisionEncoder,
    output_dir: str = "./output"
) -> Path:
    """
    Deterministically routes the document extraction based on its physical memory layout.
    """
    doc = RawDocument(file_path=file_path, file_size_bytes=file_path.stat().st_size)
    q_factor = topology_analyzer.analyze(doc)
    
    ast: MarkdownAST
    
    if q_factor >= 0.95:
        # Extract the semantic ALT text from discrete image objects in RAM
        semantic_image_map = _extract_and_encode_images(doc, vision_encoder)
        
        # Extract the O(N) spatial graph in RAM
        nodes = _extract_spatial_graph(doc)
        
        # Dispatch to the graph compiler (which will utilize the semantic_image_map)
        ast = spatial_compiler.compile_graph(nodes)
        
    else:
        # Fallback to dense tensor OCR inference
        # Note: The VisionExtractor adapter handles its own internal layout cropping
        ast = vision_extractor.extract_ast(doc)
        
    out_path = Path(output_dir) / f"{file_path.stem}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ast.content, encoding="utf-8")
    
    return out_path

def _extract_and_encode_images(document: RawDocument, encoder: VisionEncoder) -> dict[str, str]:
    """
    Traverses the C-level XREF table for discrete image objects.
    Extracts the byte stream and maps it to a semantic string via the VLM port.
    
    Returns:
        dict: Mapping of internal PDF image references to semantic ALT text.
    """
    image_semantics = {}
    pdf = fitz.open(str(document.file_path))
    try:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            image_list = page.get_images(full=True)
            
            for img in image_list:
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Execute the VLM inference sequentially to bound VRAM usage
                semantic_string = encoder.encode_tensor(image_bytes)
                image_semantics[f"xref_{xref}"] = semantic_string
    finally:
        pdf.close()
        
    return image_semantics

def _extract_spatial_graph(document: RawDocument) -> list[SpatialNode]:
    """
    Extracts the continuous vector boundaries into discrete spatial nodes.
    """
    nodes = []
    pdf = fitz.open(str(document.file_path))
    try:
        for page in pdf:
            words = page.get_text("words")
            for w in words:
                nodes.append(SpatialNode(char=w[4], x0=w[0], y0=w[1], x1=w[2], y1=w[3]))
    finally:
        pdf.close()
    return nodes
