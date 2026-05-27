import os
import sys
from pathlib import Path
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Parse .env file directly
_env_vars = dotenv_values(ENV_FILE)
# Merge with os.environ, but only if the value is not empty
for k, v in os.environ.items():
    if v:  # Only use non-empty values from os.environ
        _env_vars[k] = v

TELEGRAM_BOT_TOKEN = _env_vars.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = _env_vars.get("ANTHROPIC_API_KEY")
OUTPUT_DIR_NAME = _env_vars.get("OUTPUT_DIR", "output")
TEMPLATE_EXCEL_PATH = _env_vars.get("TEMPLATE_EXCEL_PATH", "template.xlsx")

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / OUTPUT_DIR_NAME
# TEMPLATE_EXCEL_PATH might be relative to project root (e.g., "data/template.xlsx")
TEMPLATE_EXCEL = PROJECT_ROOT / TEMPLATE_EXCEL_PATH

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")
if not TEMPLATE_EXCEL.exists():
    raise FileNotFoundError(f"Template Excel not found: {TEMPLATE_EXCEL}")

OUTPUT_DIR.mkdir(exist_ok=True)
