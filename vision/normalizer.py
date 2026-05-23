"""
Converts raw LLM JSON output → PropertyData.
Handles Japanese currency strings, dash nulls, and derived calculations.
"""
import re
from .schema import PropertyData


def parse_yen(text: str) -> int:
    """
    '33,500円' | '¥33.500' | '33500' | '-' → int
    Extracts the FIRST numeric amount (before 円 or at start of string).
    """
    if not text or str(text).strip() in ("-", "ー", "－", ""):
        return 0
    # Try: number before 円 (e.g. "1,143円（駐車場1台…）" → 1143)
    m = re.search(r"[¥￥]?\s*([\d,\.]+)\s*円", str(text))
    if m:
        return int(re.sub(r"[^\d]", "", m.group(1)))
    # Try: leading number (e.g. "33500" or "¥33,500")
    m = re.search(r"[¥￥]?\s*([\d,\.]+)", str(text))
    if m:
        return int(re.sub(r"[^\d]", "", m.group(1)))
    return 0


def parse_rate(text: str) -> float:
    """'賃料総額の2.2%又は5.5%' → 2.2"""
    match = re.search(r"(\d+\.?\d*)%", str(text))
    return float(match.group(1)) if match else 2.2


def parse_maintenance_detail(detail_text: str, fallback_total: int) -> int:
    """
    '共益費等明細：ケーブルＴＶ代金 550円\n共益費 2,000円' → 2550
    Sums all yen amounts found in the detail string.
    Falls back to fallback_total if nothing found.
    """
    if not detail_text:
        return fallback_total
    amounts = re.findall(r"[\d,\.]+円", detail_text)
    if not amounts:
        return fallback_total
    total = sum(parse_yen(a) for a in amounts)
    return total if total > 0 else fallback_total


def parse_other_fees_community(text: str) -> tuple[int, int]:
    """
    '町内会費 300円' → (other=0, community=300)
    '管理費 500円' → (other=500, community=0)
    Returns (other_base, community_fee)
    """
    community_keywords = ("自治会", "町内会", "管理組合")
    amounts = re.findall(r"([\d,\.]+)円", str(text))
    total = sum(parse_yen(a + "円") for a in amounts)
    text_lower = str(text)
    if any(k in text_lower for k in community_keywords):
        return 0, total
    return total, 0


def build_notes(prop: PropertyData) -> str:
    lines = []
    if prop.maintenance_detail:
        lines.append(f"共益費等明細：{prop.maintenance_detail}")
    if prop.guarantee_monthly_text:
        lines.append(
            f"その他費用に、月額保証料（{prop.guarantee_monthly_text}）と、"
            f"24時間サポート費用（月額）{prop.support_fee_monthly}円が必要です。"
        )
    lines.append(
        "5月12日以降に入居申込の場合、24時間サポート費用と収納手数料は不要となりますが、"
        "別途ruumサポート費用1,980円（月額）が必要です。"
    )
    return "\n".join(lines)


def normalize(raw: dict) -> PropertyData:
    """
    raw: dict as returned by LLM vision worker.
    Keys (all optional, default to "" / "0"):
        property_name, room_number, customer_name,
        move_in_date, rent_start_date,
        rent_text, parking_text, deposit_text, key_money_text,
        maintenance_text, maintenance_detail,
        other_fees_text,          ← 町内会費 etc.
        guarantee_initial_text,   ← 契約時：22,000円
        guarantee_monthly_rate,   ← "2.2%又は5.5%"
        guarantee_monthly_amount_text, ← "879円（駐車場1台…）"
        cleaning_fee_text, support_fee_text,
        key_set_text, renewal_fee_text,
        agency_fee_text,          ← if blank, computed as rent×1.1
        advertising_fee_text,
    """
    rent = parse_yen(raw.get("rent_text", "0"))
    parking = parse_yen(raw.get("parking_text", "0"))
    deposit = parse_yen(raw.get("deposit_text", "0"))
    key_money = parse_yen(raw.get("key_money_text", "0"))

    # 共益費等: use detail breakdown if available
    maintenance_raw = parse_yen(raw.get("maintenance_text", "0"))
    maintenance_detail = raw.get("maintenance_detail", "")
    maintenance = parse_maintenance_detail(maintenance_detail, maintenance_raw)

    # その他費用 split into community_fee vs other
    other_text = raw.get("other_fees_text", "")
    other_base, community_fee = parse_other_fees_community(other_text)

    # Guarantee
    guarantee_rate = parse_rate(raw.get("guarantee_monthly_rate", "2.2%"))
    guarantee_monthly_text = raw.get("guarantee_monthly_amount_text", "")
    guarantee_monthly_amount = parse_yen(guarantee_monthly_text)
    guarantee_initial = parse_yen(raw.get("guarantee_initial_text", "0"))

    # 24h support
    support_fee = parse_yen(raw.get("support_fee_text", "330円"))
    if support_fee == 0:
        support_fee = 330

    # その他費用 total = 月額保証料 + 24hサポート (+ any other fixed monthly)
    other_fees = guarantee_monthly_amount + support_fee + other_base

    # Move-in costs
    agency_fee_text = raw.get("agency_fee_text", "")
    if agency_fee_text:
        agency_fee = parse_yen(agency_fee_text)
    else:
        agency_fee = int(rent * 1.1)  # standard = 賃料×1.1（税込）

    parking_contract_fee = parse_yen(
        raw.get("parking_contract_fee_text", str(parking) + "円")
    )
    cleaning_fee = parse_yen(raw.get("cleaning_fee_text", "0"))
    key_set_fee = parse_yen(raw.get("key_set_text", "0"))

    prop = PropertyData(
        property_name=raw.get("property_name", ""),
        room_number=raw.get("room_number", ""),
        customer_name=raw.get("customer_name", ""),
        move_in_date=raw.get("move_in_date", ""),
        rent_start_date=raw.get("rent_start_date", ""),
        rent=rent,
        parking=parking,
        maintenance=maintenance,
        other_fees=other_fees,
        community_fee=community_fee,
        extra_monthly=0,
        support_fee_monthly=support_fee,
        guarantee_rate=guarantee_rate,
        key_money=key_money,
        deposit=deposit,
        agency_fee=agency_fee,
        parking_contract_fee=parking_contract_fee,
        cleaning_fee=cleaning_fee,
        guarantee_initial=guarantee_initial,
        key_set_fee=key_set_fee,
        maintenance_detail=maintenance_detail,
        guarantee_monthly_amount=guarantee_monthly_amount,
        guarantee_monthly_text=guarantee_monthly_text,
    )
    prop.notes = build_notes(prop)
    return prop
