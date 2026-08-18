from unittest.mock import patch

from core.service import process_property

RAW_EXAMPLE = {
    "property_type": "アパート",
    "floor_plan": "3DK",
    "rent_text": "42,000円",
    "parking_text": "3,300円",
    "maintenance_text": "3,000円",
    "other_fees_text": "町内会費 600円",
    "key_money_text": "-",
    "deposit_text": "-",
    "agency_fee_text": "",
    "cleaning_fee_text": "70,000円",
    "guarantee_initial_text": "22,000円",
    "guarantee_monthly_rate": "2.2%又は5.5%",
    "guarantee_monthly_amount_text": "1,119円（駐車場1台、2.2%プランの場合）",
    "support_fee_text": "1,980円",
    "key_set_text": "3,300円",
}

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


@patch("core.service.extract", return_value=RAW_EXAMPLE)
def test_process_property_matches_reference_example(mock_extract):
    result = process_property([(b"img1", "image/png"), (b"img2", "image/png")])

    assert result == EXPECTED
    mock_extract.assert_called_once_with([(b"img1", "image/png"), (b"img2", "image/png")])


RAW_WITH_MONTH_MULTIPLIER_KEY_MONEY = {
    **RAW_EXAMPLE,
    "rent_text": "82,500円",
    "key_money_text": "1ヶ月",
    "deposit_text": "0.5ヶ月",
    "agency_fee_text": "90,750円",
}


@patch("core.service.extract", return_value=RAW_WITH_MONTH_MULTIPLIER_KEY_MONEY)
def test_process_property_converts_month_multiplier_key_money_and_deposit(mock_extract):
    result = process_property([(b"img1", "image/png"), (b"img2", "image/png")])

    assert "🔑 礼金: ¥82,500" in result
    assert "🏦 敷金: ¥41,250" in result
