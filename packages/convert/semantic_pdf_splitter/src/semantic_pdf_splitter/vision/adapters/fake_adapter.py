from semantic_pdf_splitter.vision.domain.ports import VisionEncoderPort
from semantic_pdf_splitter.vision.domain.models import PhysicalImageReference, SemanticDescription

class FakeVisionEncoderAdapter(VisionEncoderPort):
    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        return SemanticDescription(
            content=f"[ALT Text] Fake deterministic extraction for {image.file_path.name}",
            metadata={"adapter": "FakeVisionEncoderAdapter"}
        )
