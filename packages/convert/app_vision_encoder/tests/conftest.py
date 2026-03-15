"""
Pytest configuration and deterministic test doubles for Contract Testing.
"""

import pytest
from pathlib import Path
from PIL import Image

from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

class FakeVisionEncoderAdapter:
    """
    Deterministic Test Double for the VisionEncoderPort.
    Bypasses PyTorch and HTTP execution to allow instantaneous contract validation.
    """
    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        return SemanticDescription(
            content=f"Semantic description of tensor at {image.file_path.name}",
            metadata={"engine": "FakeAdapter", "quantization": "none"}
        )

@pytest.fixture(scope="session")
def fake_encoder() -> VisionEncoderPort:
    return FakeVisionEncoderAdapter()

@pytest.fixture(scope="session")
def synthetic_image_tensor(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Synthesizes a minimal H x W x C matrix in RAM and flushes it to a transient OS directory.
    Guarantees zero static binary leakage into the local file system.
    """
    fixture_dir = tmp_path_factory.mktemp("fixtures")
    out_path = fixture_dir / "synthetic_graph.png"
    
    # Generate a minimal 100x100 RGB tensor
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img.save(out_path)
        
    return out_path

@pytest.fixture
def physical_image(synthetic_image_tensor: Path) -> PhysicalImageReference:
    """
    Instantiates the immutable domain entity pointing to the synthetic tensor.
    """
    return PhysicalImageReference(
        file_path=synthetic_image_tensor,
        file_size_bytes=synthetic_image_tensor.stat().st_size
    )
