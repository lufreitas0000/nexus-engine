"""
Validation suite for the PDF Topology Analyzer via Shannon Entropy.
"""

import math
from pathlib import Path
from src.domain.models import RawDocument
from src.domain.services.topology import PdfTopologyAnalyzer

def test_analyzer_identifies_pure_raster(degraded_raster_book_path: Path):
    """
    Validates that a purely rasterized PDF yields an empty/degenerate string manifold,
    collapsing H(X) -> 0 and mapping Q -> 0.0.
    """
    doc = RawDocument(
        file_path=degraded_raster_book_path, 
        file_size_bytes=degraded_raster_book_path.stat().st_size
    )
    analyzer = PdfTopologyAnalyzer()
    q_factor = analyzer.analyze(doc)
    
    assert isinstance(q_factor, float)
    assert math.isclose(q_factor, 0.0, abs_tol=0.01)

def test_analyzer_identifies_pure_vector(clean_vector_book_path: Path):
    """
    Validates that native text primitives yield natural language entropy
    (3.5 < H(X) < 5.0), mapping Q -> 1.0.
    """
    doc = RawDocument(
        file_path=clean_vector_book_path, 
        file_size_bytes=clean_vector_book_path.stat().st_size
    )
    analyzer = PdfTopologyAnalyzer()
    q_factor = analyzer.analyze(doc)
    
    assert isinstance(q_factor, float)
    assert math.isclose(q_factor, 1.0, abs_tol=0.01)
