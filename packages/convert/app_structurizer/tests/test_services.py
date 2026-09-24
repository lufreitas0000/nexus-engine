from pathlib import Path
import pytest
from app_structurizer.src.services.extraction import extract_document_to_markdown
from app_structurizer.src.domain.ports import (
    VisionExtractor,
    SpatialCompiler,
    VisionEncoder,
)
from app_structurizer.src.domain.services.topology import PdfTopologyAnalyzer
from app_structurizer.src.domain.models import MarkdownAST

from app_structurizer.src.domain.models import MarkdownAST


class MockTopologyAnalyzer(PdfTopologyAnalyzer):
    def __init__(self, q_factor: float):
        self._q_factor = q_factor

    def analyze(self, document) -> float:
        return self._q_factor


class MockSpatialCompiler(SpatialCompiler):
    def compile_graph(self, nodes) -> MarkdownAST:
        return MarkdownAST(
            content="# Simulated Chapter from SpatialCompiler", metadata={}
        )


class MockVisionEncoder(VisionEncoder):
    def encode_tensor(self, image_bytes: bytes) -> str:
        return "[ALT Text] Mock image"


def test_extract_document_to_markdown_io_piping(
    fake_extractor: VisionExtractor, degraded_raster_book_path: Path, tmp_path: Path
) -> None:
    topology_analyzer = MockTopologyAnalyzer(q_factor=0.1)  # Force VLM branch
    spatial_compiler = MockSpatialCompiler()
    vision_encoder = MockVisionEncoder()

    out_path = extract_document_to_markdown(
        file_path=degraded_raster_book_path,
        topology_analyzer=topology_analyzer,
        vision_extractor=fake_extractor,
        spatial_compiler=spatial_compiler,
        vision_encoder=vision_encoder,
        output_dir=tmp_path,
    )

    assert out_path.exists(), "The output Markdown file was not created on disk."
    assert (
        out_path.suffix == ".json"
    ), "The output file lacks the correct topological extension."

    content = out_path.read_text(encoding="utf-8")
    import json
    data = json.loads(content)
    assert "Simulated Chapter" in data["sections"][0]["content"][0]["text"], "The AST content was corrupted during I/O flush."
