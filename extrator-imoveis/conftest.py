import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # extrator-imoveis/
REPO_ROOT = ROOT.parent                          # Mirai/ (has vision/)

for path in (ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
