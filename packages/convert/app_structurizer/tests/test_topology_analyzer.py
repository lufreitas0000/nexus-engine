"""
Validation suite for the PDF Topology Analyzer.
Ensures accurate mathematical classification of PDF memory layouts.
"""

import pytest
from pathlib import Path
from src.domain.models import RawDocument

# We import the service we are ABOUT to build
from src.domain.services.topology import PdfTopologyAnalyzer, DocumentTopology

def test_analyzer_identifies_pure_raster(degraded_raster_book_path: Path):
    """
    Validates that a PDF built purely from Image XObjects yields a RASTER topology.
    """
    doc = RawDocument(file_path=degraded_raster_book_path, file_size_bytes=degraded_raster_book_path.stat().st_size)
    analyzer = PdfTopologyAnalyzer()
    
    topology = analyzer.analyze(doc)
    
    assert topology == DocumentTopology.RASTER_SCANNED

def test_analyzer_identifies_pure_vector(clean_vector_book_path: Path):
    """
    Validates that a PDF built using native text primitives yields a VECTOR topology.
    """
    doc = RawDocument(file_path=clean_vector_book_path, file_size_bytes=clean_vector_book_path.stat().st_size)
    analyzer = PdfTopologyAnalyzer()
    
    topology = analyzer.analyze(doc)
    
    assert topology == DocumentTopology.VECTOR_DIGITAL
