from pathlib import Path
import pytest
from app_vision_encoder.src.domain.models import (
    PhysicalImageReference,
    SemanticDescription,
)


def test_physical_image_reference_success(tmp_path: Path):
    file_path = tmp_path / "test_image.png"
    file_path.write_bytes(b"dummy_image_bytes")

    ref = PhysicalImageReference(file_path=file_path, file_size_bytes=17)

    assert ref.file_path == file_path
    assert ref.file_size_bytes == 17


def test_physical_image_reference_not_found():
    fake_path = Path("/tmp/does_not_exist.png")

    with pytest.raises(FileNotFoundError):
        PhysicalImageReference(file_path=fake_path, file_size_bytes=0)


def test_semantic_description_immutability():
    desc = SemanticDescription(content="A red car", metadata={"model": "fake"})

    assert desc.content == "A red car"
    assert desc.metadata == {"model": "fake"}
