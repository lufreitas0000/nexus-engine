from pathlib import Path
import fitz  # type: ignore
from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor, SpatialCompiler, SpatialNode, VisionEncoder
from src.domain.services.topology import PdfTopologyAnalyzer
from src.domain.services.ast_stitcher import AstStitcher

def extract_document_to_markdown(
    file_path: Path,
    topology_analyzer: PdfTopologyAnalyzer,
    vision_extractor: VisionExtractor,
    spatial_compiler: SpatialCompiler,
    vision_encoder: VisionEncoder,
    output_dir: Path | str = "./output"
) -> Path:
    """
    Deterministically routes the document extraction based on its physical memory layout.
    """
    doc = RawDocument(file_path=file_path, file_size_bytes=file_path.stat().st_size)
    q_factor = topology_analyzer.analyze(doc)

    ast: MarkdownAST
    
    semantic_image_map = {}

    if q_factor >= 0.95:
        semantic_image_map = _extract_and_encode_images(doc, vision_encoder)
        nodes = _extract_spatial_graph(doc)
        ast = spatial_compiler.compile_graph(nodes)
    else:
        # For raster documents, we rely on the vision extractor entirely.
        ast = vision_extractor.extract_ast(doc)
        
    # AST Stitching / Filtering Phase
    stitcher = AstStitcher()
    refined_ast = stitcher.stitch_ast(ast, semantic_image_map)

    out_dir = Path(output_dir)
    out_path = out_dir / f"{file_path.stem}.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(refined_ast.content, encoding="utf-8")
    
    return out_path

def _extract_and_encode_images(document: RawDocument, encoder: VisionEncoder) -> dict[str, str]:
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

                semantic_string = encoder.encode_tensor(image_bytes)
                image_semantics[f"xref_{xref}"] = semantic_string
    finally:
        pdf.close()

    return image_semantics

def _extract_spatial_graph(document: RawDocument) -> list[SpatialNode]:
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
