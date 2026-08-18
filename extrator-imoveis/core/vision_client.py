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
  "deposit_text": "敷金, ex: 0円 ou 0.5ヶ月 ou -",
  "key_money_text": "礼金, ex: 0円 ou 1ヶ月 ou -",
  "maintenance_text": "共益費等, ex: 3,000円",
  "maintenance_detail": "detalhamento do共益費等 se houver, cada item com seu valor em 円",
  "other_fees_text": "texto de その他費用 tal como aparece, ex: 町内会費 600円",
  "guarantee_initial_text": "保証委託料 pago no contrato, ex: 22,000円",
  "guarantee_monthly_rate": "taxa mensal do seguro, ex: 2.2%又は5.5%",
  "guarantee_monthly_amount_text": "valor mensal do 保証委託料, ex: 1,119円（駐車場1台、2.2%プランの場合）",
  "cleaning_fee_text": "クリーニング費, ex: 70,000円",
  "support_fee_text": "taxa de suporte mensal recorrente ATUALMENTE aplicável, procure com cuidado em parágrafos de 特記事項/備考, não só em tabelas — costuma aparecer embutida em frases longas. ATENÇÃO: é comum o texto mencionar DOIS valores condicionados a uma data de corte, ex: '24時間サポート費用（月額）330円が必要です。5月12日以降に入居申込の場合、24時間サポート費用と収納手数料は不要となりますが、ruumサポート費用1,980円（月額）が必要です'. Nesse padrão, o valor 'X月X日以降' (depois de tal data) é o que vale hoje, já que essa data sempre já passou — extraia esse valor (no exemplo, 1,980円, não 330円). Se não houver esse padrão de duas datas, extraia o único valor mencionado normalmente (ex: '24時間サポート費用330円' sozinho, ou '緊急駆けつけサービス550円')",
  "key_set_text": "鍵セット費, ex: 3,300円",
  "agency_fee_text": "仲介手数料, deixe \\"\\" se não aparecer explicitamente na imagem",
  "card_fee_text": "収納手数料 (taxa extra cobrada apenas se o aluguel for pago por cartão de crédito), ex: 170円. Deixe \\"\\" se não for mencionado"
}

Retorne APENAS o JSON."""


class VisionExtractionError(Exception):
    pass


def extract(images: list[tuple[bytes, str]], api_key: str | None = None) -> dict:
    if not images:
        raise VisionExtractionError("Nenhuma imagem enviada")

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise VisionExtractionError("Erro de configuração do servidor. Avise o administrador")
    client = Anthropic(api_key=key, timeout=60.0)

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
    except anthropic.APIError as exc:
        raise VisionExtractionError("Erro ao consultar a Claude API. Tente novamente") from exc

    text = None
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text = block.text
            break
    if text is None:
        raise VisionExtractionError("Claude não retornou uma resposta válida")

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise VisionExtractionError(
            "Não consegui extrair dados dessas imagens. Tente capturas mais nítidas"
        )

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise VisionExtractionError(
            "Não consegui extrair dados dessas imagens. Tente capturas mais nítidas"
        ) from exc
