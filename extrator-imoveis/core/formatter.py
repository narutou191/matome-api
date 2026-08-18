from vision.schema import PropertyData

DISCLAIMER = (
    "⚠️ Observação: estes valores são apenas uma referência inicial e podem variar. "
    "A confirmação oficial dos valores ocorre somente na etapa de intenção de contrato.\n"
    "\n"
    "📷 A precisão dos valores depende da qualidade da imagem. Para melhores resultados, "
    "prefira capturas de tela direto do portal."
)


def format_emoji(prop: PropertyData, property_type: str = "", floor_plan: str = "") -> str:
    month_total = prop.rent + prop.parking + prop.maintenance + prop.other_fees + prop.community_fee
    entry_total = (
        prop.key_money
        + prop.deposit
        + prop.agency_fee
        + prop.parking_contract_fee
        + prop.cleaning_fee
        + prop.guarantee_initial
        + prop.key_set_fee
    )
    grand_total = month_total + entry_total

    header = " ".join(part for part in (property_type, floor_plan) if part)

    lines = [
        f"🏠 {header}",
        "",
        "【月額費用】",
        f"💴 家賃: ¥{prop.rent:,}",
        f"🚗 駐車場: ¥{prop.parking:,}",
        f"🏢 共益費等: ¥{prop.maintenance:,}",
        f"📋 その他費用: ¥{prop.other_fees:,}",
        f"🏘️ 自治会費: ¥{prop.community_fee:,}",
        f"　　月合計: ¥{month_total:,}",
        "",
        "【入居時費用】",
        f"🔑 礼金: ¥{prop.key_money:,}",
        f"🏦 敷金: ¥{prop.deposit:,}",
        f"💼 仲介手数料: ¥{prop.agency_fee:,}",
        f"🅿️ 駐車場契約: ¥{prop.parking_contract_fee:,}",
        f"🧹 クリーニング費: ¥{prop.cleaning_fee:,}",
        f"🛡️ 保証委託料: ¥{prop.guarantee_initial:,}",
        f"🗝️ 鍵セット費: ¥{prop.key_set_fee:,}",
        f"　　入居時合計: ¥{entry_total:,}",
        "",
        "━━━━━━━━━━━━━━━",
        f"💰 合計金額: ¥{grand_total:,}",
        "━━━━━━━━━━━━━━━",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)
