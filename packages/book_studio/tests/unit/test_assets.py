import pytest
from pathlib import Path
from book_studio.core.schemas import ExtractionResult, Page, Block
from book_studio.core.assets import AssetManager

def test_asset_manager_routing_and_mutation(tmp_path):
    source_dir = tmp_path / "source"
    asset_dir = tmp_path / "assets"
    source_dir.mkdir()
    
    # Create a dummy image file
    dummy_img = source_dir / "diagram_1.png"
    dummy_img.touch()
    
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[
                Block(id="1", block_type="Figure", content="Here is the graph: ![diagram](diagram_1.png)")
            ])
        ]
    )
    
    manager = AssetManager(asset_dir)
    result = manager.process_and_route(raw, source_dir)
    
    # Assert physical file was routed
    assert (asset_dir / "diagram_1.png").exists()
    
    # Assert text block was mutated to the placeholder schema
    mutated_content = result.pages[0].blocks[0].content
    assert "[!figure] Asset: diagram_1.png" in mutated_content
    assert "**Alt-Text:** [AGENT_TO_GENERATE]" in mutated_content
    assert "![diagram](diagram_1.png)" not in mutated_content
