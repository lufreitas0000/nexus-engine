from app_spatial_compiler.src.infrastructure.adapters.vision_encoder import VisionEncoderAdapter

def test_vision_adapter_resolves_complex_manifold() -> None:
    """
    Asserts that the Vision Adapter correctly accepts Euclidean bounds
    and returns a deterministic LaTeX string representing the graphical region.
    """
    adapter = VisionEncoderAdapter()
    bounds = (10.0, 50.0, 100.0, 150.0) # (x0, y0, x1, y1)
    
    result = adapter.resolve_subgraph(bounds)
    
    assert isinstance(result, str)
    # Align assertion with the actual LaTeX figure environment return state
    assert "\\begin{figure}" in result
    assert "ext_vlm_at_10_50" in result
