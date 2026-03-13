"""
Validation suite for the Application Service orchestration layer.
"""

from pathlib import Path
from src.services.encoder_service import generate_semantic_ast_node
from src.domain.ports import VisionEncoderPort

def test_generate_semantic_ast_node_orchestration(
    synthetic_image_tensor: Path, 
    fake_encoder: VisionEncoderPort
) -> None:
    """
    Validates that the service correctly instantiates the domain models,
    pipes the reference through the injected dependency port, and returns the AST node.
    """
    ast_node = generate_semantic_ast_node(
        image_path=synthetic_image_tensor,
        encoder=fake_encoder
    )
    
    assert ast_node.content.startswith("Semantic description of tensor")
    assert ast_node.metadata["engine"] == "FakeAdapter"
