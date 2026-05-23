"""
Teste manual com dados extraídos das imagens DK Portal.
Simula o que o LLM Vision retornará no formato bruto.
"""
from pathlib import Path
from vision import normalize, fill_template

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Imóvel 1 — 三重県四日市市松本 | 1K | 家賃 33,500円 | 申込中
# ─────────────────────────────────────────────────────────────────────────────
raw_1 = {
    "property_name": "（物件名不明）",
    "room_number": "",
    "customer_name": "",
    "move_in_date": "",
    "rent_start_date": "2026/05/01",

    "rent_text": "33,500円",
    "parking_text": "3,300円",
    "deposit_text": "0円",
    "key_money_text": "0円",
    "maintenance_text": "2,550円",
    "maintenance_detail": "ケーブルＴＶ代金 550円\n共益費 2,000円",
    "other_fees_text": "町内会費 300円",

    "guarantee_initial_text": "22,000円",
    "guarantee_monthly_rate": "2.2%",
    "guarantee_monthly_amount_text": "879円（駐車場1台、2.2%プランの場合）",
    "cleaning_fee_text": "50,000円",
    "support_fee_text": "330円",
    "key_set_text": "3,300円",
    # 仲介手数料: 広告料 = 33,500円（特記）→ usar como agency_fee
    "agency_fee_text": "33,500円",
}

# ─────────────────────────────────────────────────────────────────────────────
# Imóvel 2 — 三重県鈴鹿市末広北 | 2LDK | 家賃 55,000円 | 募集中
# ─────────────────────────────────────────────────────────────────────────────
raw_2 = {
    "property_name": "ニュークレストールオーブリー/F1F1F1-S",
    "room_number": "",
    "customer_name": "",
    "move_in_date": "即入居可",
    "rent_start_date": "2026/05/01",

    "rent_text": "55,000円",
    "parking_text": "3,300円",
    "deposit_text": "-",
    "key_money_text": "-",
    "maintenance_text": "3,300円",
    "maintenance_detail": "共益費 3,300円",
    "other_fees_text": "町内会費 250円",

    "guarantee_initial_text": "22,000円",
    "guarantee_monthly_rate": "2.2%",
    "guarantee_monthly_amount_text": "1,367円（駐車場1台、2.2%プランの場合）",
    "cleaning_fee_text": "70,000円",
    "support_fee_text": "330円",
    "key_set_text": "3,300円",
    # 仲介手数料: 55,000 × 1.1 = 60,500（calculado automaticamente）
}

# ─────────────────────────────────────────────────────────────────────────────
# Imóvel 3 — 三重県鈴鹿市中江島町 | 2LDK | 家賃 44,000円 | 募集中
# (Este é o imóvel que aparece preenchido no template Excel de exemplo)
# ─────────────────────────────────────────────────────────────────────────────
raw_3 = {
    "property_name": "ニューマリッチ/NMS造店舗付",
    "room_number": "",
    "customer_name": "",
    "move_in_date": "即入居可",
    "rent_start_date": "2026/05/01",

    "rent_text": "44,000円",
    "parking_text": "3,300円",
    "deposit_text": "-",
    "key_money_text": "-",
    "maintenance_text": "3,850円",
    "maintenance_detail": "ケーブルＴＶ代金 550円\n共益費 3,300円",
    "other_fees_text": "町内会費 500円",

    "guarantee_initial_text": "22,000円",
    "guarantee_monthly_rate": "2.2%",
    "guarantee_monthly_amount_text": "1,143円（駐車場1台、2.2%プランの場合）",
    "cleaning_fee_text": "70,000円",
    "support_fee_text": "330円",
    "key_set_text": "3,300円",
    # 仲介手数料: 44,000 × 1.1 = 48,400（calculado automaticamente）
}


def run_test(name: str, raw: dict):
    prop = normalize(raw)
    out = fill_template(prop, OUTPUT_DIR / f"{name}.xlsx")

    # Verificação contra valores esperados
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  家賃:          {prop.rent:>8,}円")
    print(f"  駐車場:        {prop.parking:>8,}円")
    print(f"  共益費等:      {prop.maintenance:>8,}円")
    print(f"  その他費用:    {prop.other_fees:>8,}円  (保証{prop.guarantee_monthly_amount}+24h{prop.support_fee_monthly})")
    print(f"  自治会費:      {prop.community_fee:>8,}円")
    monthly_total = prop.rent + prop.parking + prop.maintenance + prop.other_fees + prop.community_fee
    print(f"  月合計:        {monthly_total:>8,}円")
    print()
    print(f"  礼金:          {prop.key_money:>8,}円")
    print(f"  敷金:          {prop.deposit:>8,}円")
    print(f"  仲介手数料:    {prop.agency_fee:>8,}円")
    print(f"  駐車場契約:    {prop.parking_contract_fee:>8,}円")
    print(f"  クリーニング:  {prop.cleaning_fee:>8,}円")
    print(f"  保証委託初期:  {prop.guarantee_initial:>8,}円")
    print(f"  鍵セット:      {prop.key_set_fee:>8,}円")
    entry_total = (prop.key_money + prop.deposit + prop.agency_fee +
                   prop.parking_contract_fee + prop.cleaning_fee +
                   prop.guarantee_initial + prop.key_set_fee)
    print(f"  入居費合計:    {entry_total:>8,}円")
    print()
    print(f"  Excel salvo: {out}")
    return prop


if __name__ == "__main__":
    p1 = run_test("imovel_1_yokkaichi_1K_33500", raw_1)
    p2 = run_test("imovel_2_suzuka_2LDK_55000", raw_2)
    p3 = run_test("imovel_3_suzuka_2LDK_44000", raw_3)

    # Validação do imóvel 3 contra o Excel de exemplo
    print("\n" + "="*60)
    print("  VALIDAÇÃO — Imóvel 3 vs Excel de exemplo")
    print("="*60)
    checks = [
        ("月合計 (小計)",
         p3.rent + p3.parking + p3.maintenance + p3.other_fees + p3.community_fee,
         53_123),
        ("仲介手数料", p3.agency_fee, 48_400),
        ("クリーニング費", p3.cleaning_fee, 70_000),
        ("契約時保証委託料", p3.guarantee_initial, 22_000),
        ("鍵セット費", p3.key_set_fee, 3_300),
    ]
    for label, got, expected in checks:
        ok = "✓" if got == expected else f"✗ (expected {expected:,})"
        print(f"  {label:20s}: {got:>8,}円  {ok}")
