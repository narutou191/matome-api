import re

from vision.normalizer import normalize, parse_yen

from core.formatter import format_emoji
from core.vision_client import extract

_MONTH_MULTIPLIER = re.compile(r"(\d+(?:\.\d+)?)\s*ヶ月")
_PRICE_RANGE = re.compile(r"[\d,]+\s*円\s*[〜~\-]\s*[\d,]+\s*円")


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


def _ambiguity_notes(raw: dict) -> list[str]:
    """Flags values the listing itself leaves conditional/ambiguous — which
    parking spot gets assigned, whether the tenant pays by credit card —
    rather than silently picking one side. Nothing here can be resolved
    from the listing text alone, so it's surfaced for human judgment
    instead of folded into the calculated total.
    """
    notes = []

    parking_text = raw.get("parking_text", "")
    if _PRICE_RANGE.search(parking_text):
        notes.append(
            f"🅿️ O estacionamento tem faixa de valores ({parking_text}) — "
            "o valor usado no cálculo acima é o mínimo. Confirme a vaga "
            "específica antes de fechar."
        )

    card_fee_text = raw.get("card_fee_text", "").strip()
    if card_fee_text and card_fee_text != "-":
        notes.append(
            f"💳 Taxa extra de {card_fee_text} se o aluguel for pago por "
            "cartão de crédito (não incluída no total acima)."
        )

    return notes


def process_property(images: list[tuple[bytes, str]]) -> str:
    raw = extract(images)

    rent = parse_yen(raw.get("rent_text", "0"))
    for field in ("key_money_text", "deposit_text"):
        raw[field] = _resolve_month_multiplier(raw.get(field, ""), rent)

    prop = normalize(raw)
    text = format_emoji(
        prop,
        property_type=raw.get("property_type", ""),
        floor_plan=raw.get("floor_plan", ""),
    )

    notes = _ambiguity_notes(raw)
    if notes:
        text += "\n\n" + "\n".join(notes)

    return text
