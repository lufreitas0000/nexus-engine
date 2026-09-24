import pytest
from app_spatial_compiler.src.domain.models import SpatialNode
from app_spatial_compiler.src.application.use_cases.markdown_synthesis import (
    MarkdownSynthesizer,
    StructuralDispatcher,
)


def test_markdown_synthesizer_basic_block():
    nodes = [
        SpatialNode(char="A", x0=10, y0=10, x1=15, y1=20, font_size=10),
        SpatialNode(char=" ", x0=15, y0=10, x1=20, y1=20, font_size=10),
        SpatialNode(char="B", x0=20, y0=10, x1=25, y1=20, font_size=10),
    ]
    synth = MarkdownSynthesizer(median_width=5.0, median_height=10.0)
    result = synth.synthesize_text(nodes)
    assert result == "A B"


def test_structural_dispatcher_detects_header():
    # Regular block
    b1 = [SpatialNode(char="T", x0=10, y0=10, x1=15, y1=20, font_size=10)]
    # Header block
    b2 = [SpatialNode(char="H", x0=10, y0=30, x1=20, y1=50, font_size=20)]

    synth = MarkdownSynthesizer(median_width=5.0, median_height=10.0)
    dispatcher = StructuralDispatcher(synth)

    ast = dispatcher.generate_ast([b1, b2])
    assert "T\n\n# H" == ast
