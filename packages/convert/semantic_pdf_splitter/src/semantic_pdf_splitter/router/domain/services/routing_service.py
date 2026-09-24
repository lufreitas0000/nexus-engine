from typing import List

from semantic_pdf_splitter.router.domain.models import RoutingDecision, RouteTarget, PageComplexityMetrics
from semantic_pdf_splitter.router.domain.ports import PageAnalyzerPort

class HybridRouter:
    def __init__(
        self,
        analyzers: List[PageAnalyzerPort],
        max_image_ratio: float = 0.3,
        max_tables: int = 0,
        min_text_density: float = 0.1
    ):
        self.analyzers = analyzers
        self.max_image_ratio = max_image_ratio
        self.max_tables = max_tables
        self.min_text_density = min_text_density

    def route_page(self, document_path: str, page_number: int) -> RoutingDecision:
        metrics = None
        for analyzer in self.analyzers:
            try:
                metrics = analyzer.extract_metrics(document_path, page_number)
                break
            except Exception:
                continue

        if not metrics:
            raise RuntimeError(f"All analyzers failed to extract metrics for page {page_number}")

        if metrics.image_area_ratio > self.max_image_ratio:
            return RoutingDecision(
                page_number=page_number,
                target=RouteTarget.VLM_COMPLEX,
                reason="Image area ratio exceeds threshold"
            )

        if metrics.table_count > self.max_tables:
            return RoutingDecision(
                page_number=page_number,
                target=RouteTarget.VLM_COMPLEX,
                reason="Table count exceeds threshold"
            )

        if metrics.equation_count > 0:
            return RoutingDecision(
                page_number=page_number,
                target=RouteTarget.VLM_COMPLEX,
                reason="Contains equations"
            )

        if metrics.text_density > self.min_text_density:
            return RoutingDecision(
                page_number=page_number,
                target=RouteTarget.FAST_TEXT,
                reason="Standard text layout"
            )

        # Default fallback for pages with near-zero text density and low images
        return RoutingDecision(
            page_number=page_number,
            target=RouteTarget.FAST_TEXT,
            reason="Low density fallback"
        )
