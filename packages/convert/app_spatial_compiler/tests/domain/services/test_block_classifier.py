import pytest
from app_spatial_compiler.src.domain.models import SpatialNode, BlockType
from app_spatial_compiler.src.application.use_cases.markdown_synthesis import (
    StructuralDispatcher,
    MarkdownSynthesizer,
)


def test_structural_dispatcher_detects_block_types():
    # 1. Standard TEXT block
    text_nodes = [
        SpatialNode(
            char="a", x0=10 + (i * 2), y0=10, x1=12 + (i * 2), y1=14, font_size=10
        )
        for i in range(50)
    ]

    # 2. HEADER block (single line, large font)
    header_nodes = [
        SpatialNode(
            char="H", x0=10 + (i * 10), y0=30, x1=20 + (i * 10), y1=50, font_size=20
        )
        for i in range(5)
    ]

    # 3. LIST block (starts with bullet)
    # The first element is the bullet. Then a larger X gap to force a space.
    list_nodes = [SpatialNode(char="-", x0=10, y0=60, x1=12, y1=64, font_size=10)] + [
        SpatialNode(
            char="x", x0=20 + (i * 2), y0=60, x1=22 + (i * 2), y1=64, font_size=10
        )
        for i in range(10)
    ]

    synth = MarkdownSynthesizer(median_width=5.0, median_height=10.0)
    dispatcher = StructuralDispatcher(synth)

    md_out = dispatcher.generate_ast([text_nodes, header_nodes, list_nodes])

    assert "# HHHHH" in md_out
    assert "a" * 50 in md_out
    assert "- xxxxxxxxxx" in md_out
