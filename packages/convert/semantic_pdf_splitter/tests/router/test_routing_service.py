import pytest

from semantic_pdf_splitter.router.domain.models import PageComplexityMetrics, RouteTarget
from semantic_pdf_splitter.router.domain.ports import PageAnalyzerPort
from semantic_pdf_splitter.router.domain.services.routing_service import HybridRouter

class MockPageAnalyzer(PageAnalyzerPort):
    def __init__(self, metrics: PageComplexityMetrics):
        self.metrics = metrics

    def extract_metrics(self, document_path: str, page_number: int) -> PageComplexityMetrics:
        return self.metrics

def test_hybrid_router_routes_to_fast_text_for_pure_text():
    metrics = PageComplexityMetrics(
        page_number=1,
        image_area_ratio=0.0,
        table_count=0,
        equation_count=0,
        text_density=0.8
    )

    analyzer = MockPageAnalyzer(metrics)
    router = HybridRouter(analyzers=[analyzer])

    decision = router.route_page("dummy_path.pdf", 1)

    assert decision.target == RouteTarget.FAST_TEXT
    assert decision.reason == "Standard text layout"

def test_hybrid_router_routes_to_vlm_for_tables():
    metrics = PageComplexityMetrics(
        page_number=1,
        image_area_ratio=0.0,
        table_count=1,
        equation_count=0,
        text_density=0.8
    )

    analyzer = MockPageAnalyzer(metrics)
    router = HybridRouter(analyzers=[analyzer])

    decision = router.route_page("dummy_path.pdf", 1)

    assert decision.target == RouteTarget.VLM_COMPLEX
    assert decision.reason == "Table count exceeds threshold"

def test_hybrid_router_routes_to_vlm_for_equations():
    metrics = PageComplexityMetrics(
        page_number=1,
        image_area_ratio=0.0,
        table_count=0,
        equation_count=1,
        text_density=0.8
    )

    analyzer = MockPageAnalyzer(metrics)
    router = HybridRouter(analyzers=[analyzer])

    decision = router.route_page("dummy_path.pdf", 1)

    assert decision.target == RouteTarget.VLM_COMPLEX
    assert decision.reason == "Contains equations"

def test_hybrid_router_routes_to_vlm_for_high_image_ratio():
    metrics = PageComplexityMetrics(
        page_number=1,
        image_area_ratio=0.5, # Exceeds default 0.3
        table_count=0,
        equation_count=0,
        text_density=0.1
    )

    analyzer = MockPageAnalyzer(metrics)
    router = HybridRouter(analyzers=[analyzer])

    decision = router.route_page("dummy_path.pdf", 1)

    assert decision.target == RouteTarget.VLM_COMPLEX
    assert decision.reason == "Image area ratio exceeds threshold"

def test_hybrid_router_fallback_to_fast_text_for_low_density():
    metrics = PageComplexityMetrics(
        page_number=1,
        image_area_ratio=0.1,
        table_count=0,
        equation_count=0,
        text_density=0.05 # Below default min_text_density 0.1
    )

    analyzer = MockPageAnalyzer(metrics)
    router = HybridRouter(analyzers=[analyzer])

    decision = router.route_page("dummy_path.pdf", 1)

    assert decision.target == RouteTarget.FAST_TEXT
    assert decision.reason == "Low density fallback"
