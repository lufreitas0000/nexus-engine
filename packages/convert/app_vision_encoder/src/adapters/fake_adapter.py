from src.domain.models import PhysicalImageReference, SemanticDescription
from src.domain.ports import VisionEncoderPort

class FakeVisionEncoderAdapter(VisionEncoderPort):
    """
    Deterministic test double that immediately returns semantic text
    without allocating VRAM or making network calls.
    """
    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        return SemanticDescription(
            content=f"[ALT Text] Fake deterministic extraction for {image.file_path.name}",
            metadata={"adapter": "FakeVisionEncoderAdapter"}
        )
