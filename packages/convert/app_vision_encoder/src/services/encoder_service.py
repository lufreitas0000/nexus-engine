# app_vision_encoder/src/services/encoder_service.py
from pathlib import Path
from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

def generate_semantic_ast_node(
    image_path: Path,
    encoder: VisionEncoderPort
) -> SemanticDescription:
    """
    Orchestrates the domain transformation sequence.
    Validates the physical memory pointer and delegates the tensor inference.
    """
    reference = PhysicalImageReference(
        file_path=image_path,
        file_size_bytes=image_path.stat().st_size
    )

    return encoder.encode_manifold(reference)
