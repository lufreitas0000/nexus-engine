"""
Domain Service for Mathematical PDF Topology Analysis.
Calculates the density of vector text to classify the memory layout of the document.
"""

import enum
import fitz  # type: ignore
from src.domain.models import RawDocument

class DocumentTopology(enum.Enum):
    """Discrete states representing the physical layout of the PDF manifold."""
    RASTER_SCANNED = "RASTER_SCANNED"
    VECTOR_DIGITAL = "VECTOR_DIGITAL"
    # We will add DIGITAL_ACADEMIC (with equations) in a future iteration

class PdfTopologyAnalyzer:
    """
    Analyzes the byte-stream of a PDF to determine if it is an image-based scan
    or a modern vector-based document.
    """
    
    def analyze(self, document: RawDocument) -> DocumentTopology:
        """
        Calculates the vector text density heuristic.
        
        Args:
            document: Validated pointer to the PDF file.
            
        Returns:
            DocumentTopology: The classified state of the document.
        """
        # Open the C-level document struct
        doc = fitz.open(str(document.file_path))
        
        total_text_length = 0
        total_pages = len(doc)
        
        if total_pages == 0:
            return DocumentTopology.RASTER_SCANNED
            
        # O(N) traversal of the pages to extract native UTF-8 vectors
        for page in doc:
            text = page.get_text()
            total_text_length += len(text.strip())
            
        doc.close()
        
        avg_text_per_page = total_text_length / total_pages
        
        # Mathematical Heuristic:
        # If a page averages less than 50 characters of native text, 
        # the text is trapped inside a raster image matrix.
        if avg_text_per_page < 50:
            return DocumentTopology.RASTER_SCANNED
            
        return DocumentTopology.VECTOR_DIGITAL
