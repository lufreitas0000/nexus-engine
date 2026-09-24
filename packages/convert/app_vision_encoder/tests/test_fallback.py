import pytest

def test_vision_encoder_fallback(tmp_path):
    # Simulate a fake adapter fallback when Gemini rate-limits
    from app_vision_encoder.src.adapters.fake_adapter import FakeVisionEncoderAdapter
    from app_vision_encoder.src.domain.models import PhysicalImageReference
    from pathlib import Path
    
    test_img = tmp_path / "test.png"
    test_img.write_bytes(b"fake image data")
    
    adapter = FakeVisionEncoderAdapter()
    result = adapter.encode_manifold(PhysicalImageReference(file_path=test_img, file_size_bytes=100))
    
    assert "Fake deterministic extraction" in result.content
