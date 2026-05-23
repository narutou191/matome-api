from dataclasses import dataclass, field


@dataclass
class PropertyData:
    # --- Header ---
    property_name: str = ""
    room_number: str = ""
    customer_name: str = ""
    move_in_date: str = ""      # YYYY/MM/DD
    rent_start_date: str = ""   # YYYY/MM/DD

    # --- Monthly recurring (前家賃等) ---
    rent: int = 0               # 家賃
    parking: int = 0            # 駐車場使用料
    maintenance: int = 0        # 共益費等
    other_fees: int = 0         # その他費用 = 月額保証料 + 24hサポート
    community_fee: int = 0      # 自治会費
    extra_monthly: int = 0      # 追加行（空白）

    # --- Hidden helper cells (pro-rata formulas) ---
    support_fee_monthly: int = 330      # 24時間サポート費用（月額）
    guarantee_rate: float = 2.2         # 保証料率 %

    # --- Move-in costs (入居時発生費用等) ---
    key_money: int = 0              # 礼金
    deposit: int = 0                # 敷金
    agency_fee: int = 0             # 仲介手数料
    parking_contract_fee: int = 0   # 駐車場契約手数料
    cleaning_fee: int = 0           # クリーニング費
    guarantee_initial: int = 0      # 契約時保証委託料
    key_set_fee: int = 0            # 鍵セット費
    extra_entry_1: int = 0
    extra_entry_2: int = 0

    # --- Notes ---
    notes: str = ""

    # --- Raw source fields (for notes auto-generation) ---
    maintenance_detail: str = ""    # e.g. "ケーブルTV 550円 / 共益費 3,300円"
    guarantee_monthly_amount: int = 0   # 月額保証委託料（数値）
    guarantee_monthly_text: str = ""    # "1,143円（駐車場1台、2.2%プランの場合）"
