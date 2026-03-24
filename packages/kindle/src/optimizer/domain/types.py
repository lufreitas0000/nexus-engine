from dataclasses import dataclass

@dataclass(frozen=True)
class TargetHardwareConstraints:
    width: int = 1264
    height: int = 1680
    dpi: int = 300
    margin_crop: str = "0.2"

@dataclass(frozen=True)
class OptimizerConfig:
    binary_path: str
    hardware: TargetHardwareConstraints
    fallback_chunk_pages: int = 20
    timeout_per_page_sec: float = 15.0
    large_document_threshold: int = 50
