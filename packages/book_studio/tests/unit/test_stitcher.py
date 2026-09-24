from book_studio.core.schemas import ExtractionResult, Page, Block
from book_studio.core.stitcher import CrossPageStitcher

def test_stitcher_hyphenation():
    stitcher = CrossPageStitcher()
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[Block(id="1", block_type="Text", content="The wave-")]),
            Page(page_number=2, blocks=[Block(id="2", block_type="Text", content="function collapses.")])
        ]
    )
    result = stitcher.stitch(raw)
    assert len(result.pages[0].blocks) == 0
    assert result.pages[1].blocks[0].content == "The wavefunction collapses."

def test_stitcher_sentence_continuation():
    stitcher = CrossPageStitcher()
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[Block(id="1", block_type="Text", content="Consider a particle")]),
            Page(page_number=2, blocks=[Block(id="2", block_type="Text", content="moving in a potential.")])
        ]
    )
    result = stitcher.stitch(raw)
    assert result.pages[1].blocks[0].content == "Consider a particle moving in a potential."

def test_stitcher_math_environment():
    stitcher = CrossPageStitcher()
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[Block(id="1", block_type="Text", content=r"Where \begin{equation} E =")]),
            Page(page_number=2, blocks=[Block(id="2", block_type="Text", content=r"mc^2 \end{equation} is the energy.")])
        ]
    )
    result = stitcher.stitch(raw)
    assert result.pages[1].blocks[0].content == r"Where \begin{equation} E = mc^2 \end{equation} is the energy."

def test_stitcher_no_stitching_needed():
    stitcher = CrossPageStitcher()
    raw = ExtractionResult(
        pages=[
            Page(page_number=1, blocks=[Block(id="1", block_type="Text", content="This sentence ends properly.")]),
            Page(page_number=2, blocks=[Block(id="2", block_type="Text", content="This is a new paragraph.")])
        ]
    )
    result = stitcher.stitch(raw)
    assert result.pages[0].blocks[0].content == "This sentence ends properly."
    assert result.pages[1].blocks[0].content == "This is a new paragraph."
