from src.domain.types import TargetHardwareConstraints

KINDLE_MODELS = {
    "Oasis": TargetHardwareConstraints(
        width=1264,
        height=1680,
        dpi=300,
        margin_crop="0.3",
        downrate="0.5",
        bits_per_channel="2"
    ),
    "Paperwhite": TargetHardwareConstraints(
        width=1236,
        height=1648,
        dpi=300,
        margin_crop="0.2",
        downrate="0.5",
        bits_per_channel="2"
    ),
    "Scribe": TargetHardwareConstraints(
        width=1860,
        height=2480,
        dpi=300,
        margin_crop="0.1",
        downrate="0.5",
        bits_per_channel="2"
    ),
    "Basic": TargetHardwareConstraints(
        width=1072,
        height=1448,
        dpi=300,
        margin_crop="0.4",
        downrate="0.5",
        bits_per_channel="2"
    )
}
