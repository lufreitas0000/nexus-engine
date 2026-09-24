from pathlib import Path
from app_vision_encoder.src.services.ast_generation import generate_semantic_ast_node
from app_vision_encoder.src.adapters.fake_adapter import FakeVisionEncoderAdapter


def test_generate_semantic_ast_node_orchestration(tmp_path: Path):
    file_path = tmp_path / "diagram.png"
    file_path.write_bytes(b"image")

    adapter = FakeVisionEncoderAdapter()

    result = generate_semantic_ast_node(file_path, adapter)

    assert "Fake deterministic extraction for diagram.png" in result.content
