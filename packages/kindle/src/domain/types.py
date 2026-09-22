from dataclasses import dataclass

@dataclass(frozen=True)
class TargetHardwareConstraints:
    width: int = 1264
    height: int = 1680
    dpi: int = 300
    margin_crop: str = "0.3"
    downrate: str = "0.5"
    bits_per_channel: str = "2"
