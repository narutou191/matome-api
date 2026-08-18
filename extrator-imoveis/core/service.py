import re

from vision.normalizer import normalize, parse_yen

from core.formatter import format_emoji
from core.vision_client import extract

_MONTH_MULTIPLIER = re.compile(r"(\d+(?:\.\d+)?)\s*ヶ月")


def _resolve_month_multiplier(text: str, rent: int) -> str:
    """'1ヶ月' / '0.5ヶ月' (common 礼金/敷金 notation meaning N months' rent)
    → an absolute yen string, so downstream yen-parsing doesn't misread the
    leading digit as the amount itself. Text without this pattern (a plain
    yen amount, '-', etc.) passes through unchanged.
    """
    if not text:
        return text
    match = _MONTH_MULTIPLIER.search(text)
    if not match:
        return text
    multiplier = float(match.group(1))
    return f"{int(rent * multiplier)}円"


def process_property(images: list[tuple[bytes, str]]) -> str:
    raw = extract(images)

    rent = parse_yen(raw.get("rent_text", "0"))
    for field in ("key_money_text", "deposit_text"):
        raw[field] = _resolve_month_multiplier(raw.get(field, ""), rent)

    prop = normalize(raw)
    return format_emoji(
        prop,
        property_type=raw.get("property_type", ""),
        floor_plan=raw.get("floor_plan", ""),
    )
