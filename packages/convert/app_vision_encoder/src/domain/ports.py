from typing import Protocol
from app_vision_encoder.src.domain.models import (
    PhysicalImageReference,
    SemanticDescription,
)


class VisionEncoderPort(Protocol):
    """
    Enforces structural subtyping for side-effectful ML mapping.
    Maps an R^(H x W x C) tensor into a discrete semantic string.
    """

    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription: ...
