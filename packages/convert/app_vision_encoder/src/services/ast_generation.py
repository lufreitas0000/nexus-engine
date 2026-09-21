from pathlib import Path
from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

def generate_semantic_ast_node(image_path: Path, encoder: VisionEncoderPort) -> SemanticDescription:
    """
    Application Service orchestrating the pipeline: validates the pointer,
    delegates effectful mapping to the encoder, and returns the discrete state.
    """
    image_ref = PhysicalImageReference(
        file_path=image_path,
        file_size_bytes=image_path.stat().st_size
    )
    return encoder.encode_manifold(image_ref)
