from pathlib import Path
from semantic_pdf_splitter.vision.adapters.fake_adapter import FakeVisionEncoderAdapter
from semantic_pdf_splitter.vision.domain.models import PhysicalImageReference

def test_fake_adapter_returns_semantic_description(tmp_path: Path):
    file_path = tmp_path / "test_diagram.png"
    file_path.write_bytes(b"dummy")
    image = PhysicalImageReference(file_path=file_path, file_size_bytes=5)
    
    adapter = FakeVisionEncoderAdapter()
    result = adapter.encode_manifold(image)
    
    assert "[ALT Text] Fake deterministic extraction" in result.content
    assert result.metadata["adapter"] == "FakeVisionEncoderAdapter"
