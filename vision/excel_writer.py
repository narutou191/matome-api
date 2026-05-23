"""
Fills the DK Portal Excel template with PropertyData.

Cell map (Sheet1):
  Header
    E6  ← property_name         (merged E6:K6)
    E7  ← room_number
    B4  ← customer_name         (merged B4:C4)
    E8  ← move_in_date          (merged E8:G8)
    E9  ← rent_start_date       (merged E9:G9)

  前家賃等  (monthly recurring)
    F20 ← target_month          "05" etc.
    F21 ← rent                  家賃
    F22 ← parking               駐車場使用料
    F23 ← maintenance           共益費等
    F24 ← other_fees            その他費用
    F25 ← community_fee         自治会費
    F26 ← extra_monthly         (usually 0 / blank)

  Hidden helper cells (pro-rata formulas reference these)
    S21 ← rent                  (same as F21)
    S24 ← support_fee_monthly   24時間サポート費用
    S25 ← guarantee_rate        2.2 / 5.5

  入居時発生費用等
    O29 ← key_money             礼金
    O30 ← deposit               敷金
    O31 ← agency_fee            仲介手数料
    O32 ← parking_contract_fee  駐車場契約手数料
    O33 ← cleaning_fee          クリーニング費
    O34 ← guarantee_initial     契約時保証委託料
    O35 ← key_set_fee           鍵セット費
    O36 ← extra_entry_1
    O37 ← extra_entry_2

  Notes
    C42 ← notes                 (merged C42:P44)
"""
import shutil
from pathlib import Path
import openpyxl
from .schema import PropertyData


TEMPLATE_PATH = Path(__file__).parent.parent / "data" / "template.xlsx"


def _target_month(rent_start_date: str) -> str:
    """'2026/05/01' → '05'"""
    parts = rent_start_date.replace("-", "/").split("/")
    if len(parts) >= 2:
        return parts[1].zfill(2)
    return ""


def fill_template(prop: PropertyData, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    shutil.copy2(TEMPLATE_PATH, output_path)

    wb = openpyxl.load_workbook(output_path)
    ws = wb["Sheet1"]

    def w(cell: str, value):
        ws[cell] = value

    # Header
    w("E6", prop.property_name)
    w("E7", prop.room_number)
    w("B4", prop.customer_name)
    w("E8", prop.move_in_date)
    w("E9", prop.rent_start_date)

    # Target month for 前家賃等
    month = _target_month(prop.rent_start_date) or _target_month(prop.move_in_date)
    if month:
        w("F20", month)

    # Monthly recurring
    w("F21", prop.rent)
    w("F22", prop.parking)
    w("F23", prop.maintenance)
    w("F24", prop.other_fees)
    w("F25", prop.community_fee)
    w("F26", prop.extra_monthly if prop.extra_monthly else None)

    # Hidden helper cells
    w("S21", prop.rent)
    w("S24", prop.support_fee_monthly)
    w("S25", prop.guarantee_rate)

    # Move-in costs
    w("O29", prop.key_money)
    w("O30", prop.deposit)
    w("O31", prop.agency_fee)
    w("O32", prop.parking_contract_fee)
    w("O33", prop.cleaning_fee)
    w("O34", prop.guarantee_initial)
    w("O35", prop.key_set_fee)
    if prop.extra_entry_1:
        w("O36", prop.extra_entry_1)
    if prop.extra_entry_2:
        w("O37", prop.extra_entry_2)

    # Notes
    if prop.notes:
        w("C42", prop.notes)

    wb.save(output_path)
    return output_path
