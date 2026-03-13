"""
Validation suite for the pure Domain layer.
Ensures structural subtyping adherence and state immutability.
"""

import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError

from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

def test_physical_image_reference_validates_pointer(synthetic_image_tensor: Path) -> None:
    """
    Asserts that a valid physical tensor reference can be instantiated,
    mapping the filesystem pointer accurately to the system RAM/Disk boundary.
    """
    ref = PhysicalImageReference(
        file_path=synthetic_image_tensor,
        file_size_bytes=synthetic_image_tensor.stat().st_size
    )
    assert ref.file_path == synthetic_image_tensor
    assert ref.file_size_bytes > 0

def test_physical_image_reference_rejects_null_manifold(tmp_path: Path) -> None:
    """
    Asserts that attempting to map an invalid physical tensor raises a fatal exception,
    preventing degenerate state propagation into the VLM adapter.
    """
    missing_tensor = tmp_path / "null_manifold.png"
    with pytest.raises(FileNotFoundError):
        PhysicalImageReference(file_path=missing_tensor, file_size_bytes=0)

def test_domain_state_immutability(physical_image: PhysicalImageReference) -> None:
    """
    Mathematically guarantees that the domain state cannot be altered post-instantiation,
    preventing side effects during tensor routing.
    """
    with pytest.raises(FrozenInstanceError):
        # We explicitly violate the type checker to assert runtime CPython memory immutability
        physical_image.file_size_bytes = 9999  # type: ignore

def test_fake_encoder_satisfies_protocol(
    fake_encoder: VisionEncoderPort,
    physical_image: PhysicalImageReference
) -> None:
    """
    Validates the deterministic Fake correctly satisfies the VisionEncoderPort
    and strictly maps the PhysicalImageReference to a SemanticDescription.
    """
    ast_node = fake_encoder.encode_manifold(physical_image)
    
    assert isinstance(ast_node, SemanticDescription)
    assert ast_node.content.startswith("Semantic description of tensor")
    assert ast_node.metadata["engine"] == "FakeAdapter"
