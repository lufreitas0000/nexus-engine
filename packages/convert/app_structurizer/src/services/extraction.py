"""
Application Service (Use Case) layer.
Coordinates the flow of data between the filesystem I/O and the mathematically pure Domain.
"""

from pathlib import Path
from src.domain.models import RawDocument
from src.domain.ports import VisionExtractor

def extract_document_to_markdown(
    file_path: Path,
    extractor: VisionExtractor,
    output_dir: Path
) -> Path:
    """
    Orchestrates the transformation of a physical PDF artifact into a physical 
    Markdown artifact via an injected machine learning port.
    
    Args:
        file_path: The absolute path to the target PDF tensor.
        extractor: The structural subtype satisfying the VisionExtractor protocol.
        output_dir: The directory where the resulting Markdown AST will be flushed.
        
    Returns:
        Path: The absolute path to the successfully generated Markdown file.
    """
    # 1. Map continuous file to validated Domain object
    doc = RawDocument(
        file_path=file_path,
        file_size_bytes=file_path.stat().st_size
    )
    
    # 2. Execute the neural network forward pass (or Fake mapping)
    ast = extractor.extract_ast(doc)
    
    # 3. I/O: Flush the discrete Abstract Syntax Tree to non-volatile storage
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{file_path.stem}.md"
    
    out_file.write_text(ast.content, encoding="utf-8")
    
    return out_file
