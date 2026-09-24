from typing import Optional
from app_vision_encoder.src.domain.models import (
    PhysicalImageReference,
    SemanticDescription,
)
from app_vision_encoder.src.domain.ports import VisionEncoderPort


class GeminiExternalAdapter(VisionEncoderPort):
    """
    Delegates the VLM tensor mapping to the Google Gemini API.
    To be fully implemented in a later phase. Currently acts as a structural stub.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription:
        # 1. Read bytes from image.file_path
        # 2. Encode to Base64
        # 3. HTTP Request to Gemini via `httpx`
        # 4. Map JSON response back to SemanticDescription
        return SemanticDescription(
            content="[ALT Text] (Stub) Gemini output pending implementation",
            metadata={"adapter": "GeminiExternalAdapter"},
        )
