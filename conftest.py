import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent  # Mirai/ root
EXTRATOR_IMOVEIS = ROOT / "extrator-imoveis"

for path in (EXTRATOR_IMOVEIS, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
