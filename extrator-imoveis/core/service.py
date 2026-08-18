from vision.normalizer import normalize

from core.formatter import format_emoji
from core.vision_client import extract


def process_property(images: list[tuple[bytes, str]]) -> str:
    raw = extract(images)
    prop = normalize(raw)
    return format_emoji(
        prop,
        property_type=raw.get("property_type", ""),
        floor_plan=raw.get("floor_plan", ""),
    )
