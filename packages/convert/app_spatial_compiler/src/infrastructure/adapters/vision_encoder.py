import time
from app_spatial_compiler.src.domain.ports import EquationFallbackPort

class VisionEncoderAdapter(EquationFallbackPort):
    """
    Adapter for external VLM delegation. 
    Simulates the transformation of Euclidean voids into LaTeX/Markdown descriptions.
    """
    def resolve_subgraph(self, bounds: tuple[float, float, float, float]) -> str:
        # Simulate network latency and inference overhead of a VLM
        time.sleep(0.1)
        x0, y0, x1, y1 = bounds
        # Deterministic mock response for TDD validation
        return f"\\begin{{figure}}[ext_vlm_at_{int(x0)}_{int(y0)}]\n% Graphical region resolved\n\\end{{figure}}"
