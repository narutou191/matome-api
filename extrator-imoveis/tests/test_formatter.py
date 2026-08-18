from vision.schema import PropertyData
from core.formatter import format_emoji

EXPECTED = (
    "🏠 アパート 3DK\n"
    "\n"
    "【月額費用】\n"
    "💴 家賃: ¥42,000\n"
    "🚗 駐車場: ¥3,300\n"
    "🏢 共益費等: ¥3,000\n"
    "📋 その他費用: ¥3,099\n"
    "🏘️ 自治会費: ¥600\n"
    "　　月合計: ¥51,999\n"
    "\n"
    "【入居時費用】\n"
    "🔑 礼金: ¥0\n"
    "🏦 敷金: ¥0\n"
    "💼 仲介手数料: ¥46,200\n"
    "🅿️ 駐車場契約: ¥3,300\n"
    "🧹 クリーニング費: ¥70,000\n"
    "🛡️ 保証委託料: ¥22,000\n"
    "🗝️ 鍵セット費: ¥3,300\n"
    "　　入居時合計: ¥144,800\n"
    "\n"
    "━━━━━━━━━━━━━━━\n"
    "💰 合計金額: ¥196,799\n"
    "━━━━━━━━━━━━━━━\n"
    "\n"
    "⚠️ Observação: estes valores são apenas uma referência inicial e podem variar. "
    "A confirmação oficial dos valores ocorre somente na etapa de intenção de contrato.\n"
    "\n"
    "📷 A precisão dos valores depende da qualidade da imagem. Para melhores resultados, "
    "prefira capturas de tela direto do portal."
)


def test_format_emoji_matches_reference_output():
    prop = PropertyData(
        rent=42000,
        parking=3300,
        maintenance=3000,
        other_fees=3099,
        community_fee=600,
        key_money=0,
        deposit=0,
        agency_fee=46200,
        parking_contract_fee=3300,
        cleaning_fee=70000,
        guarantee_initial=22000,
        key_set_fee=3300,
    )

    result = format_emoji(prop, property_type="アパート", floor_plan="3DK")

    assert result == EXPECTED


def test_format_emoji_header_skips_missing_parts():
    prop = PropertyData()
    result = format_emoji(prop, property_type="", floor_plan="1LDK")
    assert result.startswith("🏠 1LDK\n")
