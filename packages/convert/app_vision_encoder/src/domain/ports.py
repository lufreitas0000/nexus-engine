"""
Structural Subtyping (Protocols) for the Vision Encoder bounded context.
Enforces strict Dependency Inversion for local ML models and external APIs.
"""

from typing import Protocol
from src.domain.models import PhysicalImageReference, SemanticDescription

class VisionEncoderPort(Protocol):
    r"""
    Defines the mathematical mapping f: R^{H x W x C} -> \Sigma^*.
    All ML adapters (quantized local VLMs or external APIs) must satisfy this contract.
    """
    def encode_manifold(self, image: PhysicalImageReference) -> SemanticDescription: ...
