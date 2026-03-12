"""
Infrastructure Adapter for Local ML Inference.
Maps the pure domain structures to the marker-pdf/PyTorch tensor operations.
"""

from typing import Any, Dict, Optional
import time

from src.domain.models import RawDocument, MarkdownAST
from src.domain.ports import VisionExtractor

class MarkerVisionAdapter:
    """
    Implements the VisionExtractor protocol using the local marker-pdf library.
    Utilizes lazy-loading for the PyTorch models to prevent premature VRAM/RAM exhaustion.
    """
    
    def __init__(self) -> None:
        # We hold the model pointers as None until the first forward pass.
        self._models: Optional[Any] = None

    def _load_models_lazily(self) -> None:
        """
        Allocates the neural network weights into system memory.
        This is a blocking, heavy I/O operation executed only once.
        """
        if self._models is None:
            # Delayed import to prevent PyTorch from bloating the module namespace 
            # if this adapter is instantiated but never used.
            from marker.models import load_all_models # type: ignore
            
            # Loads Surya (Layout) and Texify (Math OCR) into the PyTorch runtime.
            self._models = load_all_models()

    def extract_ast(self, document: RawDocument) -> MarkdownAST:
        """
        Executes the tensor transformation from physical PDF to discrete Markdown.
        
        Args:
            document: Validated pointer to the PDF file.
            
        Returns:
            MarkdownAST: The topological Markdown representation.
        """
        from marker.convert import convert_single_pdf # type: ignore
        
        self._load_models_lazily()
        
        start_time = time.time()
        
        # Execute the forward pass. 
        # marker-pdf expects a string path and the loaded model pointers.
        full_text, _, out_meta = convert_single_pdf(
            str(document.file_path), 
            self._models
        )
        
        execution_time = time.time() - start_time
        
        # Map the output back to our pure Domain DTO
        return MarkdownAST(
            content=full_text,
            metadata={
                "engine": "marker-pdf",
                "execution_time_seconds": f"{execution_time:.2f}",
                "pages_processed": str(out_meta.get("pages", 0))
            }
        )
