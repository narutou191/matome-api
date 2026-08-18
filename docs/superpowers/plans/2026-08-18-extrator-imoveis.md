# Extrator de Imóveis (Telegram Mini App) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `extrator-imoveis/` — a Telegram bot that opens a Mini App where the user uploads 2 screenshots of a Japanese rental listing and gets back a cost summary formatted with emojis, using the already-validated calculation logic from `vision/normalizer.py`.

**Architecture:** `core/` holds the business logic (Claude Vision call, formatting) shared by everything; `web/` is a FastAPI app that serves the upload page and exposes `POST /api/process`, and doubles as the Telegram Mini App surface; `telegram_bot/` is a minimal bot whose only job is to open the Mini App via a `web_app` button. `vision.normalizer.normalize()` and `vision.schema.PropertyData` are imported from the existing `vision/` package at the repo root — not duplicated.

**Tech Stack:** Python 3.11, FastAPI + uvicorn, `anthropic` SDK (Claude Vision), `python-telegram-bot`, pytest + pytest-asyncio.

## Global Constraints

- New project lives entirely under `extrator-imoveis/` at the repo root — no existing files outside it are modified except `.gitignore` (one line added).
- v1 is Telegram-only: `web/index.html` only needs to work correctly inside the Telegram Mini App WebView, not as a standalone public page.
- Exactly 2 images per property, sent together in a **single** Claude Vision API call (not 2 separate calls).
- The Claude API key lives server-side in `extrator-imoveis/.env` (`ANTHROPIC_API_KEY`) — the browser/Mini App never sees it.
- All money calculations (agency_fee = rent×1.1 when blank, other_fees = guarantee_monthly + support_fee, community_fee detection, etc.) come from `vision.normalizer.normalize()` — do not reimplement this logic.
- Pinned dependency versions (matching what's already installed/used elsewhere in this repo): `fastapi==0.136.0`, `uvicorn==0.45.0`, `pydantic==2.13.3`, `anthropic==0.104.1`, `python-telegram-bot==22.7`, `python-dotenv==1.2.2`, `python-multipart==0.0.26`. Dev: `pytest==9.0.3`, `pytest-asyncio==1.4.0`.
- Output text format is byte-exact to the example in the spec (`docs/superpowers/specs/2026-08-18-extrator-imoveis-design.md`) — emoji, section headers, `━━━` separators, and the two-line disclaimer at the end.

---

### Task 1: Project scaffolding + bridge to `vision/`

**Files:**
- Create: `extrator-imoveis/core/__init__.py` (empty)
- Create: `extrator-imoveis/web/__init__.py` (empty)
- Create: `extrator-imoveis/telegram_bot/__init__.py` (empty)
- Create: `extrator-imoveis/conftest.py`
- Create: `extrator-imoveis/tests/__init__.py` (empty)
- Create: `extrator-imoveis/tests/test_scaffolding.py`
- Create: `extrator-imoveis/requirements.txt`
- Create: `extrator-imoveis/.env.example`
- Modify: `.gitignore` (repo root) — add `extrator-imoveis/.env`

**Interfaces:**
- Produces: `conftest.py` puts `extrator-imoveis/` and the repo root on `sys.path`, so every later task can do `from core.xxx import yyy` and `from vision.xxx import yyy` from anywhere under `extrator-imoveis/`.

- [ ] **Step 1: Create the folder structure and empty package markers**

```bash
mkdir -p "extrator-imoveis/core" "extrator-imoveis/web" "extrator-imoveis/telegram_bot" "extrator-imoveis/tests"
touch "extrator-imoveis/core/__init__.py" "extrator-imoveis/web/__init__.py" "extrator-imoveis/telegram_bot/__init__.py" "extrator-imoveis/tests/__init__.py"
```

- [ ] **Step 2: Write the failing scaffolding test**

`extrator-imoveis/tests/test_scaffolding.py`:
```python
def test_vision_package_is_importable():
    from vision.schema import PropertyData
    from vision.normalizer import normalize

    prop = PropertyData(rent=1000)
    assert prop.rent == 1000
    assert callable(normalize)
```

- [ ] **Step 3: Run it to confirm it fails**

Run (from repo root): `cd extrator-imoveis && python -m pytest tests/test_scaffolding.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'vision'`

- [ ] **Step 4: Add `conftest.py` to bridge imports**

`extrator-imoveis/conftest.py`:
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # extrator-imoveis/
REPO_ROOT = ROOT.parent                          # Mirai/ (has vision/)

for path in (ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
```

- [ ] **Step 5: Run the test again to confirm it passes**

Run: `cd extrator-imoveis && python -m pytest tests/test_scaffolding.py -v`
Expected: PASS

- [ ] **Step 6: Add `requirements.txt`**

`extrator-imoveis/requirements.txt`:
```
fastapi==0.136.0
uvicorn==0.45.0
pydantic==2.13.3
anthropic==0.104.1
python-telegram-bot==22.7
python-dotenv==1.2.2
python-multipart==0.0.26
pytest==9.0.3
pytest-asyncio==1.4.0
```

- [ ] **Step 7: Add `.env.example`**

`extrator-imoveis/.env.example`:
```
# Claude API (server-side only, never exposed to the browser)
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
VISION_MODEL=claude-sonnet-5

# Telegram bot
TELEGRAM_BOT_TOKEN=seu_token_do_botfather_aqui
# Public HTTPS URL where web/app.py is hosted (Render etc.) — required by Telegram Mini Apps
WEBAPP_URL=https://seu-app.onrender.com
```

- [ ] **Step 8: Ignore the real `.env`**

Append one line to the repo root `.gitignore`:
```
extrator-imoveis/.env
```

- [ ] **Step 9: Commit**

```bash
git add extrator-imoveis/ .gitignore
git commit -m "chore: scaffold extrator-imoveis project structure"
```

---

### Task 2: `core/formatter.py` — emoji-formatted output

**Files:**
- Create: `extrator-imoveis/core/formatter.py`
- Test: `extrator-imoveis/tests/test_formatter.py`

**Interfaces:**
- Consumes: `vision.schema.PropertyData` (existing dataclass — fields: `rent, parking, maintenance, other_fees, community_fee, key_money, deposit, agency_fee, parking_contract_fee, cleaning_fee, guarantee_initial, key_set_fee`, all `int`).
- Produces: `format_emoji(prop: PropertyData, property_type: str = "", floor_plan: str = "") -> str`, used by Task 4 (`core/service.py`).

- [ ] **Step 1: Write the failing test**

`extrator-imoveis/tests/test_formatter.py`:
```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `cd extrator-imoveis && python -m pytest tests/test_formatter.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.formatter'`

- [ ] **Step 3: Implement `core/formatter.py`**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `cd extrator-imoveis && python -m pytest tests/test_formatter.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/core/formatter.py extrator-imoveis/tests/test_formatter.py
git commit -m "feat: add emoji formatter for property cost summary"
```

---

### Task 3: `core/vision_client.py` — Claude Vision extraction

**Files:**
- Create: `extrator-imoveis/core/vision_client.py`
- Test: `extrator-imoveis/tests/test_vision_client.py`

**Interfaces:**
- Produces: `extract(images: list[tuple[bytes, str]], api_key: str | None = None) -> dict` and `VisionExtractionError` exception, used by Task 4 (`core/service.py`). Each tuple in `images` is `(raw_bytes, mime_type)` e.g. `(b"...", "image/png")`.

- [ ] **Step 1: Write the failing tests**

`extrator-imoveis/tests/test_vision_client.py`:
```python
from unittest.mock import MagicMock, patch

import anthropic
import httpx
import pytest

from core.vision_client import extract, VisionExtractionError


def _fake_response(text):
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


def _fake_httpx_response(status_code):
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return httpx.Response(status_code=status_code, request=request)


@patch("core.vision_client.Anthropic")
def test_extract_parses_json_from_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response(
        'Aqui está o JSON:\n{"rent_text": "42,000円", "property_type": "アパート"}'
    )
    mock_anthropic_cls.return_value = mock_client

    result = extract([(b"fake-image-bytes", "image/png")], api_key="test-key")

    assert result == {"rent_text": "42,000円", "property_type": "アパート"}
    mock_client.messages.create.assert_called_once()


@patch("core.vision_client.Anthropic")
def test_extract_sends_all_images_plus_prompt(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response("{}")
    mock_anthropic_cls.return_value = mock_client

    extract(
        [(b"img-one", "image/png"), (b"img-two", "image/jpeg")],
        api_key="test-key",
    )

    _, kwargs = mock_client.messages.create.call_args
    content = kwargs["messages"][0]["content"]
    assert len(content) == 3  # 2 images + 1 text prompt
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1]["source"]["media_type"] == "image/jpeg"
    assert content[2]["type"] == "text"


@patch("core.vision_client.Anthropic")
def test_extract_raises_when_no_json_found(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response(
        "desculpe, não consegui ler a imagem"
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Não consegui extrair"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


def test_extract_raises_when_no_images():
    with pytest.raises(VisionExtractionError):
        extract([], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_authentication_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.AuthenticationError(
        "invalid api key", response=_fake_httpx_response(401), body=None
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="configuração do servidor"):
        extract([(b"fake-image-bytes", "image/png")], api_key="bad-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_rate_limit_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.RateLimitError(
        "rate limited", response=_fake_httpx_response(429), body=None
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Limite de requisições"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_timeout_error(mock_anthropic_cls):
    mock_client = MagicMock()
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    mock_client.messages.create.side_effect = anthropic.APITimeoutError(request=request)
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Demorou muito"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `cd extrator-imoveis && python -m pytest tests/test_vision_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.vision_client'`

- [ ] **Step 3: Implement `core/vision_client.py`**

```python
import base64
import json
import os
import re

import anthropic
from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-5"

PROMPT = """Você é um especialista em imóveis japoneses. Analise estas capturas de tela \
de um anúncio imobiliário (podem ser 2 imagens complementares do mesmo imóvel) e extraia \
os dados em um único JSON válido, sem nenhum texto antes ou depois.

Campos (use "" quando o dado não existir em nenhuma das imagens):
{
  "property_type": "tipo do imóvel, ex: アパート, マンション",
  "floor_plan": "planta, ex: 3DK, 1LDK",
  "property_name": "nome do prédio ou endereço",
  "room_number": "número do apto, ex: 2C",
  "rent_text": "家賃, ex: 42,000円",
  "parking_text": "駐車場使用料, ex: 3,300円 ou -",
  "deposit_text": "敷金, ex: 0円 ou -",
  "key_money_text": "礼金, ex: 0円 ou -",
  "maintenance_text": "共益費等, ex: 3,000円",
  "maintenance_detail": "detalhamento do共益費等 se houver, cada item com seu valor em 円",
  "other_fees_text": "texto de その他費用 tal como aparece, ex: 町内会費 600円",
  "guarantee_initial_text": "保証委託料 pago no contrato, ex: 22,000円",
  "guarantee_monthly_rate": "taxa mensal do seguro, ex: 2.2%又は5.5%",
  "guarantee_monthly_amount_text": "valor mensal do 保証委託料, ex: 1,119円（駐車場1台、2.2%プランの場合）",
  "cleaning_fee_text": "クリーニング費, ex: 70,000円",
  "support_fee_text": "taxa de suporte mensal, ex: ruumサポート費用1,980円 ou 24時間サポート費用330円",
  "key_set_text": "鍵セット費, ex: 3,300円",
  "agency_fee_text": "仲介手数料, deixe \\"\\" se não aparecer explicitamente na imagem"
}

Retorne APENAS o JSON."""


class VisionExtractionError(Exception):
    pass


def extract(images: list[tuple[bytes, str]], api_key: str | None = None) -> dict:
    if not images:
        raise VisionExtractionError("Nenhuma imagem enviada")

    client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            },
        }
        for image_bytes, mime_type in images
    ]
    content.append({"type": "text", "text": PROMPT})

    try:
        response = client.messages.create(
            model=os.environ.get("VISION_MODEL", DEFAULT_MODEL),
            max_tokens=1024,
            messages=[{"role": "user", "content": content}],
        )
    except anthropic.AuthenticationError as exc:
        raise VisionExtractionError(
            "Erro de configuração do servidor. Avise o administrador"
        ) from exc
    except anthropic.RateLimitError as exc:
        raise VisionExtractionError(
            "Limite de requisições atingido. Aguarde um momento"
        ) from exc
    except (anthropic.APITimeoutError, anthropic.APIConnectionError) as exc:
        raise VisionExtractionError("Demorou muito para responder. Tente novamente") from exc

    text = response.content[0].text
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise VisionExtractionError(
            "Não consegui extrair dados dessas imagens. Tente capturas mais nítidas"
        )

    return json.loads(match.group(0))
```

This is the single place that translates every failure mode from the spec's error table (auth, rate limit, timeout, unparseable response) into one `VisionExtractionError` type — `web/app.py` (Task 5) only needs to catch that one exception to produce the right HTTP 400 + message for all of them.

- [ ] **Step 4: Run tests to confirm they pass**

Run: `cd extrator-imoveis && python -m pytest tests/test_vision_client.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/core/vision_client.py extrator-imoveis/tests/test_vision_client.py
git commit -m "feat: add Claude Vision client for property image extraction"
```

---

### Task 4: `core/service.py` — orchestration

**Files:**
- Create: `extrator-imoveis/core/service.py`
- Test: `extrator-imoveis/tests/test_service.py`

**Interfaces:**
- Consumes: `core.vision_client.extract(images) -> dict` (Task 3), `vision.normalizer.normalize(raw) -> PropertyData` (existing), `core.formatter.format_emoji(prop, property_type, floor_plan) -> str` (Task 2).
- Produces: `process_property(images: list[tuple[bytes, str]]) -> str`, used by Task 5 (`web/app.py`).

- [ ] **Step 1: Write the failing test**

`extrator-imoveis/tests/test_service.py`:
```python
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
```

- [ ] **Step 2: Run test to confirm it fails**

Run: `cd extrator-imoveis && python -m pytest tests/test_service.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.service'`

- [ ] **Step 3: Implement `core/service.py`**

```python
from vision.normalizer import normalize

from core.formatter import format_emoji
from core.vision_client import extract


def process_property(images: list[tuple[bytes, str]]) -> str:
    raw = extract(images)
    prop = normalize(raw)
    return format_emoji(
        prop,
        property_type=raw.get("property_type", ""),
        floor_plan=raw.get("floor_plan", ""),
    )
```

- [ ] **Step 4: Run test to confirm it passes**

Run: `cd extrator-imoveis && python -m pytest tests/test_service.py -v`
Expected: PASS. This is the key end-to-end proof that the real `vision.normalizer.normalize()` calculations (agency_fee = 42,000×1.1, other_fees = 1,119+1,980, etc.) produce exactly the reference output — only `extract()` is mocked, everything downstream is real.

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/core/service.py extrator-imoveis/tests/test_service.py
git commit -m "feat: wire vision extraction, normalizer and formatter into process_property"
```

---

### Task 5: `web/app.py` — FastAPI endpoint

**Files:**
- Create: `extrator-imoveis/web/app.py`
- Test: `extrator-imoveis/tests/test_web_app.py`

**Interfaces:**
- Consumes: `core.service.process_property(images) -> str` (Task 4), `core.vision_client.VisionExtractionError` (Task 3).
- Produces: FastAPI `app` object with `GET /`, `GET /health`, `POST /api/process` — consumed by Task 6 (frontend) and Task 8 (deploy/README).

- [ ] **Step 1: Write the failing tests**

`extrator-imoveis/tests/test_web_app.py`:
```python
import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from web.app import app

client = TestClient(app)


def _fake_image(name):
    return (name, io.BytesIO(b"fake-bytes"), "image/png")


@patch("web.app.process_property", return_value="🏠 resultado de teste")
def test_process_returns_formatted_result(mock_process):
    response = client.post(
        "/api/process",
        files=[
            ("images", _fake_image("foto1.png")),
            ("images", _fake_image("foto2.png")),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {"result": "🏠 resultado de teste"}
    mock_process.assert_called_once()


def test_process_rejects_wrong_image_count():
    response = client.post("/api/process", files=[("images", _fake_image("foto1.png"))])

    assert response.status_code == 400
    assert "2 capturas" in response.json()["detail"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `cd extrator-imoveis && python -m pytest tests/test_web_app.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'web.app'`

- [ ] **Step 3: Implement `web/app.py`**

```python
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from core.service import process_property
from core.vision_client import VisionExtractionError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_HTML = Path(__file__).resolve().parent / "index.html"


@app.get("/")
def serve_index():
    return FileResponse(INDEX_HTML)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process(images: list[UploadFile] = File(...)):
    if len(images) != 2:
        raise HTTPException(
            status_code=400,
            detail="Envie as 2 capturas de tela (物件概要 e その他詳細)",
        )

    payload = [(await img.read(), img.content_type or "image/png") for img in images]

    try:
        result = process_property(payload)
    except VisionExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"result": result}
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `cd extrator-imoveis && python -m pytest tests/test_web_app.py -v`
Expected: 2 pass, 1 fails (`GET /` needs `index.html` to exist — that's Task 6). If `test_health_check` and the two `/api/process` tests pass, that confirms this task's scope is done; `index.html` arrives in the next task.

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/web/app.py extrator-imoveis/tests/test_web_app.py
git commit -m "feat: add FastAPI endpoint for property image processing"
```

---

### Task 6: `web/index.html` — Mini App upload UI

**Files:**
- Create: `extrator-imoveis/web/index.html`

**Interfaces:**
- Consumes: `POST /api/process` (Task 5) via `fetch` with `multipart/form-data`, field name `images` (repeated twice).
- Produces: the page FastAPI serves at `GET /` (Task 5's `serve_index`), and the URL Telegram's `web_app` button opens (Task 7).

- [ ] **Step 1: Write `web/index.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Extrator de Imóveis</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: -apple-system, system-ui, sans-serif;
    max-width: 480px;
    margin: 0 auto;
    padding: 16px;
    background: var(--tg-theme-bg-color, #ffffff);
    color: var(--tg-theme-text-color, #111111);
  }
  h1 { font-size: 1.2rem; }
  .drop-zone {
    border: 2px dashed #999;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    margin-bottom: 12px;
    cursor: pointer;
  }
  .drop-zone.filled { border-color: #2ea043; }
  input[type="file"] { display: none; }
  button {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 10px;
    background: var(--tg-theme-button-color, #2ea043);
    color: var(--tg-theme-button-text-color, #ffffff);
    font-size: 1rem;
    margin-top: 8px;
  }
  button:disabled { opacity: 0.5; }
  pre {
    white-space: pre-wrap;
    word-break: break-word;
    background: rgba(127, 127, 127, 0.1);
    border-radius: 10px;
    padding: 12px;
    margin-top: 16px;
  }
  .error {
    background: #ffe1e1;
    color: #a30000;
    border-radius: 10px;
    padding: 12px;
    margin-top: 12px;
  }
  .hidden { display: none; }
</style>
</head>
<body>
  <h1>🏠 Extrator de Imóveis</h1>
  <p>Envie as 2 capturas de tela do anúncio (物件概要 e その他詳細).</p>

  <div class="drop-zone" id="zone1" onclick="document.getElementById('file1').click()">
    <span id="zone1-label">📷 Captura 1 (物件概要)</span>
    <input type="file" id="file1" accept="image/*">
  </div>

  <div class="drop-zone" id="zone2" onclick="document.getElementById('file2').click()">
    <span id="zone2-label">📷 Captura 2 (その他詳細)</span>
    <input type="file" id="file2" accept="image/*">
  </div>

  <button id="submit-btn" disabled>Processar</button>

  <div id="error" class="error hidden"></div>
  <pre id="result" class="hidden"></pre>
  <button id="copy-btn" class="hidden">📋 Copiar</button>

<script>
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
  }

  const file1 = document.getElementById('file1');
  const file2 = document.getElementById('file2');
  const submitBtn = document.getElementById('submit-btn');
  const errorBox = document.getElementById('error');
  const resultBox = document.getElementById('result');
  const copyBtn = document.getElementById('copy-btn');

  function updateZoneLabel(input, zoneId, labelId, fallback) {
    const label = document.getElementById(labelId);
    label.textContent = input.files.length ? `✅ ${input.files[0].name}` : fallback;
    document.getElementById(zoneId).classList.toggle('filled', input.files.length > 0);
  }

  function refreshState() {
    updateZoneLabel(file1, 'zone1', 'zone1-label', '📷 Captura 1 (物件概要)');
    updateZoneLabel(file2, 'zone2', 'zone2-label', '📷 Captura 2 (その他詳細)');
    submitBtn.disabled = !(file1.files.length && file2.files.length);
  }

  file1.addEventListener('change', refreshState);
  file2.addEventListener('change', refreshState);

  submitBtn.addEventListener('click', async () => {
    errorBox.classList.add('hidden');
    resultBox.classList.add('hidden');
    copyBtn.classList.add('hidden');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Processando...';

    const formData = new FormData();
    formData.append('images', file1.files[0]);
    formData.append('images', file2.files[0]);

    try {
      const response = await fetch('/api/process', { method: 'POST', body: formData });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao processar as imagens');
      }

      resultBox.textContent = data.result;
      resultBox.classList.remove('hidden');
      copyBtn.classList.remove('hidden');
    } catch (err) {
      errorBox.textContent = `❌ ${err.message}`;
      errorBox.classList.remove('hidden');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Processar';
    }
  });

  copyBtn.addEventListener('click', async () => {
    await navigator.clipboard.writeText(resultBox.textContent);
    copyBtn.textContent = '✅ Copiado!';
    setTimeout(() => { copyBtn.textContent = '📋 Copiar'; }, 1500);
  });
</script>
</body>
</html>
```

- [ ] **Step 2: Run the web app test suite to confirm `GET /` now passes too**

Run: `cd extrator-imoveis && python -m pytest tests/test_web_app.py -v`
Expected: all pass (the `serve_index` route from Task 5 can now find `index.html`).

- [ ] **Step 3: Start the server locally**

```bash
cd extrator-imoveis
ANTHROPIC_API_KEY=dummy VISION_MODEL=claude-sonnet-5 python -m uvicorn web.app:app --reload --port 8000
```

- [ ] **Step 4: Manually verify the UI in the browser**

Use the Browser pane (`preview_start` with `{url: "http://localhost:8000"}`), then verify:
- Page loads, title "🏠 Extrator de Imóveis" visible
- "Processar" button is disabled until both zones have a file
- Selecting only 1 image and forcing a submit is not possible (button stays disabled) — confirms client-side gating works
- Selecting 2 tiny dummy images and clicking "Processar" shows either a result or an error banner (with `ANTHROPIC_API_KEY=dummy` it will show a `❌` error from the Claude API auth failure — that confirms the error path renders correctly without needing a real key/cost)

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/web/index.html
git commit -m "feat: add Mini App upload UI for property screenshots"
```

---

### Task 7: `telegram_bot/bot.py` — bot with Mini App button

**Files:**
- Create: `extrator-imoveis/telegram_bot/bot.py`
- Test: `extrator-imoveis/tests/test_telegram_bot.py`

**Interfaces:**
- Consumes: `WEBAPP_URL` env var (points to the hosted `web/app.py`, Task 8).
- Produces: `build_application() -> telegram.ext.Application` and the `start` handler, run via `python -m telegram_bot.bot`.

- [ ] **Step 1: Write the failing test**

`extrator-imoveis/tests/test_telegram_bot.py`:
```python
import os
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("WEBAPP_URL", "https://example.com/miniapp")

from telegram_bot.bot import start


@pytest.mark.asyncio
async def test_start_sends_webapp_button():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    await start(update, context)

    update.message.reply_text.assert_called_once()
    _, kwargs = update.message.reply_text.call_args
    markup = kwargs["reply_markup"]
    button = markup.inline_keyboard[0][0]
    assert button.web_app.url == "https://example.com/miniapp"
    assert "capturas" in button.text.lower()
```

- [ ] **Step 2: Run test to confirm it fails**

Run: `cd extrator-imoveis && python -m pytest tests/test_telegram_bot.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'telegram_bot.bot'`

(Our local package is deliberately named `telegram_bot/`, not `telegram/` — the installed library `python-telegram-bot` is itself imported as top-level `telegram`, and `conftest.py` puts `extrator-imoveis/` first on `sys.path`. If our local folder were also called `telegram/`, it would shadow the real library and break the `from telegram import ...` line inside our own bot module.)

- [ ] **Step 3: Implement `telegram_bot/bot.py`**

```python
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

WELCOME_TEXT = (
    "🏠 Envie as 2 capturas de tela do imóvel (物件概要 e その他詳細) "
    "pelo botão abaixo para calcular os custos automaticamente."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    webapp_url = os.environ["WEBAPP_URL"]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📤 Enviar capturas do imóvel", web_app=WebAppInfo(url=webapp_url))]]
    )
    await update.message.reply_text(WELCOME_TEXT, reply_markup=keyboard)


def build_application() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    return application


if __name__ == "__main__":
    build_application().run_polling()
```

- [ ] **Step 4: Run test to confirm it passes**

Run: `cd extrator-imoveis && python -m pytest tests/test_telegram_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/telegram_bot/bot.py extrator-imoveis/tests/test_telegram_bot.py
git commit -m "feat: add Telegram bot with Mini App launch button"
```

---

### Task 8: Deployment config + README

**Files:**
- Create: `extrator-imoveis/render.yaml`
- Create: `extrator-imoveis/README.md`
- Test: manual smoke check (no new automated test — this task is config/docs)

**Interfaces:**
- Consumes: `web/app.py` (Task 5), `telegram_bot/bot.py` (Task 7), `.env.example` (Task 1).

- [ ] **Step 1: Write `render.yaml`**

```yaml
services:
  - type: web
    name: extrator-imoveis
    runtime: python-3.11
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn web.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: VISION_MODEL
        value: claude-sonnet-5
```

- [ ] **Step 2: Write `README.md`**

```markdown
# Extrator de Imóveis (Telegram Mini App)

Envie 2 capturas de tela de um anúncio de imóvel japonês (物件概要 + その他詳細) e receba
o resumo de custos formatado, calculado com a mesma lógica validada do projeto VISION.

## Como funciona

1. Usuário manda `/start` pro bot no Telegram
2. Bot responde com um botão que abre o Mini App (a página web deste projeto, dentro do Telegram)
3. Usuário faz upload das 2 imagens no Mini App
4. O servidor chama a Claude Vision API, aplica os cálculos de `vision/normalizer.py`
   e devolve o texto formatado, exibido na hora com botão de copiar

## Rodar localmente

```bash
cd extrator-imoveis
pip install -r requirements.txt
cp .env.example .env   # preencha ANTHROPIC_API_KEY
python -m uvicorn web.app:app --reload --port 8000
```

Abra `http://localhost:8000` no navegador pra testar o upload sem precisar do Telegram.

## Testes

```bash
cd extrator-imoveis
python -m pytest -v
```

## Configurar o bot do Telegram

1. Fale com [@BotFather](https://t.me/BotFather) no Telegram, crie um bot novo, copie o token
2. Preencha `TELEGRAM_BOT_TOKEN` no `.env`
3. Depois de hospedar `web/app.py` publicamente (veja "Deploy" abaixo), preencha `WEBAPP_URL`
   com a URL pública (ex: `https://extrator-imoveis.onrender.com`)
4. Rode o bot: `python -m telegram_bot.bot`

## Deploy

Hospedado no Render via `render.yaml` (mesmo padrão do `matome_api.py` na raiz do repo):

1. Conectar o repositório no Render, apontando pra pasta `extrator-imoveis/`
2. Configurar a env var `ANTHROPIC_API_KEY` no painel do Render (não fica no `render.yaml` por segurança)
3. Depois do deploy, copiar a URL pública gerada pro `WEBAPP_URL` do bot

O bot em si (`telegram_bot/bot.py`) roda separado — local (mini PC 24/7) ou onde for mais conveniente —
só precisa conseguir falar com a API do Telegram e conhecer a `WEBAPP_URL` pública.
```

- [ ] **Step 3: Smoke-test the full local boot**

```bash
cd extrator-imoveis
ANTHROPIC_API_KEY=dummy python -m uvicorn web.app:app --port 8000 &
sleep 2
curl -s http://localhost:8000/health
kill %1
```

Expected output: `{"status":"ok"}`

- [ ] **Step 4: Run the full test suite one last time**

Run: `cd extrator-imoveis && python -m pytest -v`
Expected: all tests across all 7 previous tasks pass together.

- [ ] **Step 5: Commit**

```bash
git add extrator-imoveis/render.yaml extrator-imoveis/README.md
git commit -m "docs: add deployment config and README for extrator-imoveis"
```
