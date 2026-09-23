from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PhysicalImageReference:
    """
    Acts as a deterministic pointer to a physical tensor manifold without
    loading the entire uncompressed RGB matrix into system RAM eagerly.
    """
    file_path: Path
    file_size_bytes: int

    def __post_init__(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Image tensor not found at {self.file_path}")

@dataclass(frozen=True)
class SemanticDescription:
    """
    The mapped result in the discrete string space.
    """
    content: str
    metadata: dict[str, str]
