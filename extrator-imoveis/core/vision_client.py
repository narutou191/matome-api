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
