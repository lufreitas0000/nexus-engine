from typing import Callable, Any
from pathlib import Path

class PipelineOrchestrator:
    """
    Coordinates the execution flow of the semantic PDF pipeline components.
    It sequentially calls the extractor (router/structurizer), spatial compiler,
    and vision encoder, acting purely as an integration point above bounded contexts.
    """
    def __init__(
        self,
        extractor_fn: Callable[[Path], Any],
        spatial_fn: Callable[[Any], Any],
        vision_fn: Callable[[Any], Any]
    ):
        self.extractor_fn = extractor_fn
        self.spatial_fn = spatial_fn
        self.vision_fn = vision_fn

    def process(self, pdf_path: Path) -> Any:
        """
        Executes the sequence:
        1. Extract data (markdown/manifold) from PDF.
        2. Compile spatial topology from extracted data.
        3. Resolve final AST (e.g. vision replacement) from compiled spatial data.
        """
        # Step 1: Extract (Structurizer/Router)
        extracted_data = self.extractor_fn(pdf_path)

        # Step 2: Spatial Compilation
        spatial_ast = self.spatial_fn(extracted_data)

        # Step 3: Vision Encoding/AST Finalization
        final_ast = self.vision_fn(spatial_ast)

        return final_ast
