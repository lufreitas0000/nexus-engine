import pytest
from src.domain.models import MarkdownAST
from src.domain.services.ast_stitcher import AstStitcher

def test_ast_stitcher_strips_images_preserves_captions():
    # Setup the initial state
    raw_content = "Here is a graph: ![Graph 1](data:image/png;base64,...)\nAnd a standard link: [Google](http://google.com)"
    initial_ast = MarkdownAST(content=raw_content, metadata={})

    # Execute the pure mapping function
    stitcher_service = AstStitcher()
    refined_ast = stitcher_service.stitch_ast(initial_ast, {})

    # Assert the deterministic topological change
    assert "[ALT Text] Graph 1" in refined_ast.content
    assert "data:image/png" not in refined_ast.content
    assert "[Google](http://google.com)" in refined_ast.content # Links remain untouched

def test_ast_stitcher_injects_semantic_text():
    # Setup the initial state with a matched xref
    raw_content = "![Data Chart](xref_123.png)"
    initial_ast = MarkdownAST(content=raw_content, metadata={})

    semantics = {"xref_123": "A bar chart showing sales."}

    # Execute
    stitcher_service = AstStitcher()
    refined_ast = stitcher_service.stitch_ast(initial_ast, semantics)

    # Assert replacement includes semantic text
    assert "[ALT Text] Data Chart - A bar chart showing sales." in refined_ast.content

def test_ast_stitcher_injects_semantic_text_no_caption():
    # Setup the initial state with no caption
    raw_content = "![](xref_456.jpg)"
    initial_ast = MarkdownAST(content=raw_content, metadata={})

    semantics = {"xref_456": "A photograph of a cat."}

    # Execute
    stitcher_service = AstStitcher()
    refined_ast = stitcher_service.stitch_ast(initial_ast, semantics)

    # Assert replacement includes semantic text only
    assert "[ALT Text] A photograph of a cat." in refined_ast.content

def test_ast_stitcher_no_caption_no_semantics():
    # Setup the initial state with no caption and no matched semantics
    raw_content = "![](unknown_image.jpg)"
    initial_ast = MarkdownAST(content=raw_content, metadata={})

    # Execute
    stitcher_service = AstStitcher()
    refined_ast = stitcher_service.stitch_ast(initial_ast, {})

    # Assert fallback
    assert "[ALT Text]" in refined_ast.content
    assert "unknown_image" not in refined_ast.content
