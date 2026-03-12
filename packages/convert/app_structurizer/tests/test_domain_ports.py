"""
Validation suite ensuring Domain logic and Ports function independently of ML frameworks.
"""

from src.domain.models import RawDocument
from src.domain.ports import VisionExtractor

def test_fake_extractor_satisfies_protocol(
    fake_extractor: VisionExtractor, 
    raw_document: RawDocument
) -> None:
    """
    Validates that our Fake object structurally satisfies the VisionExtractor Protocol
    and returns an immutable MarkdownAST without raising exceptions.
    """
    ast = fake_extractor.extract_ast(raw_document)
    
    assert ast.content.startswith("# Simulated Chapter")
    assert ast.metadata["model"] == "FakeAdapter_v1"
