from typing import Iterator
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTComponent
from app_spatial_compiler.src.domain.models import SpatialNode

class PDFExtractorAdapter:
    """
    Infrastructure adapter implementing Direct Memory Access (DMA)
    over PDF layout streams to extract character-level spatial manifolds.
    """
    def extract_nodes(self, pdf_path: str) -> list[SpatialNode]:
        nodes: list[SpatialNode] = []
        for page_layout in extract_pages(pdf_path):
            nodes.extend(self._process_layout_element(page_layout))
        return nodes

    def _process_layout_element(self, element: LTComponent) -> Iterator[SpatialNode]:
        if isinstance(element, LTChar):
            yield SpatialNode(
                char=element.get_text(),
                x0=float(element.x0),
                y0=float(element.y0),
                x1=float(element.x1),
                y1=float(element.y1),
                font_size=float(element.size)
            )
        elif hasattr(element, "__iter__"):
            for child in element:
                yield from self._process_layout_element(child)
