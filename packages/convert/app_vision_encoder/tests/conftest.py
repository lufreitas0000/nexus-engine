"""
Pytest configuration and deterministic test doubles for Contract Testing.
"""

import pytest
from pathlib import Path
from PIL import Image

from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

FIXTURE_DIR = Path(__file__).parent / "fixtures"

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
def synthetic_image_tensor() -> Path:
    """
    Synthesizes a minimal H x W x C matrix in RAM and flushes it to disk
    to simulate the upstream crop artifact from the layout detector.
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURE_DIR / "synthetic_graph.png"
    
    if not out_path.exists():
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
