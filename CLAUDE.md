# Projeto VISION

Pipeline local de IA para processar imagens de imóveis japoneses (DK Portal, prints, fotos, PDFs),
extrair dados, normalizar e gerar Excel no template oficial. Roda 100% local, 24/7.

O usuário é corretor de imóveis no Japão. Comunica em português (brasileiro).
Mini PC disponível: Ryzen 9 6900H, 32 GB RAM (Windows). Também usa Mac.

---

## Status atual

- **Fase 1: CONCLUÍDA** — normalizer + excel_writer funcionando, validado contra template real
- **Fase 2: PRÓXIMA** — integrar Ollama (LLM Vision) para processar imagens automaticamente
- **Fase 3: FUTURA** — FastAPI + Redis/RQ (fila de jobs)
- **Fase 4: FUTURA** — Integrações (WhatsApp, CRM, monitoramento)

---

## Estrutura do projeto

```
Mirai/
├── vision/
│   ├── __init__.py          # exports: PropertyData, normalize, fill_template
│   ├── schema.py            # PropertyData dataclass (todos os campos do template)
│   ├── normalizer.py        # raw LLM JSON → PropertyData (parse_yen, textos JP)
│   └── excel_writer.py      # PropertyData → preenche template.xlsx
├── data/
│   └── template.xlsx        # Template oficial (Sheet1, células B2:S51)
├── output/                  # Excels gerados (não versionar)
├── test_properties.py       # Teste com 3 imóveis reais do DK Portal
└── CLAUDE.md                # Este arquivo
```

---

## Como rodar

```bash
pip install openpyxl
python test_properties.py
```

---

## Arquitetura dos 6 módulos (visão completa)

```
Upload (imagem/PDF)
    → API Gateway (FastAPI)  POST /vision/upload
    → Fila (Redis + RQ)      job_id criado
    → Worker de Visão        Ollama (LLaVA ou Qwen-VL 7B) → JSON bruto
    → Normalizador           JSON bruto → PropertyData (schema padronizado)
    → Gerador de Excel       PropertyData → imovel_{id}.xlsx
    → API de Resultado       GET /vision/result/{job_id} → JSON + link Excel
```

---

## Contrato de dados

### Entrada do normalizer (raw LLM JSON)
```json
{
  "property_name": "ニューマリッチ/NMS造店舗付",
  "room_number": "2C",
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
  "agency_fee_text": ""
}
```

### Saída do normalizer (PropertyData → campos principais)
```
rent                 家賃
parking              駐車場使用料
maintenance          共益費等 (soma dos itens do maintenance_detail)
other_fees           月額保証料 + 24hサポート
community_fee        自治会費 / 町内会費
support_fee_monthly  24時間サポート費用 (padrão: 330)
guarantee_rate       2.2 ou 5.5
key_money            礼金
deposit              敷金
agency_fee           仲介手数料 (se vazio → rent × 1.1)
parking_contract_fee 駐車場契約手数料
cleaning_fee         クリーニング費
guarantee_initial    契約時保証委託料
key_set_fee          鍵セット費
```

---

## Mapeamento de células do template Excel (Sheet1)

### Cabeçalho
| Célula | Campo |
|--------|-------|
| B4 | customer_name (様) |
| E6 | property_name (merged E6:K6) |
| E7 | room_number |
| E8 | move_in_date (merged E8:G8) |
| E9 | rent_start_date (merged E9:G9) |

### 前家賃等 (mensalidade)
| Célula | Campo |
|--------|-------|
| F20 | target_month ("05" etc.) |
| F21 | rent — 家賃 |
| F22 | parking — 駐車場使用料 |
| F23 | maintenance — 共益費等 |
| F24 | other_fees — その他費用 |
| F25 | community_fee — 自治会費 |
| F26 | extra_monthly (geralmente vazio) |
| S21 | rent (célula oculta, usada em fórmulas de pro-rata) |
| S24 | support_fee_monthly (célula oculta) |
| S25 | guarantee_rate % (célula oculta) |

### 入居時発生費用等 (custos de entrada)
| Célula | Campo |
|--------|-------|
| O29 | key_money — 礼金 |
| O30 | deposit — 敷金 |
| O31 | agency_fee — 仲介手数料 |
| O32 | parking_contract_fee — 駐車場契約手数料 |
| O33 | cleaning_fee — クリーニング費 |
| O34 | guarantee_initial — 契約時保証委託料 |
| O35 | key_set_fee — 鍵セット費 |
| O36 | extra_entry_1 |
| O37 | extra_entry_2 |

### Observações
| Célula | Campo |
|--------|-------|
| C42 | notes (merged C42:P44) |

### Células calculadas (não escrever — fórmulas do template)
- O19 = SUM(O13:O18) — subtotal pro-rata primeiro mês
- O27 = SUM(O21:O26) — subtotal mês cheio
- O38 = SUM(O29:O37) — subtotal entrada
- M40 = O19+O27+O38 — **TOTAL GERAL**

---

## Validação confirmada (imóvel 3 vs template real)

| Campo | Valor |
|-------|-------|
| 月合計 小計 | 53,123円 ✓ |
| 仲介手数料 | 48,400円 ✓ |
| クリーニング費 | 70,000円 ✓ |
| 契約時保証委託料 | 22,000円 ✓ |
| 鍵セット費 | 3,300円 ✓ |

---

## Próxima tarefa (Fase 2) — LLM Vision

Integrar Ollama para processar imagens automaticamente:

1. Instalar Ollama: https://ollama.ai
2. Baixar modelo: `ollama pull llava` ou `ollama pull qwen2-vl`
3. Criar `vision/llm_worker.py` que:
   - Recebe caminho de imagem ou URL
   - Envia para Ollama com prompt especializado em imóveis JP
   - Retorna o raw JSON no formato esperado pelo `normalize()`

### Prompt base para o LLM (imóveis japoneses)
O prompt deve instruir o modelo a extrair os campos em JSON:
`rent_text`, `parking_text`, `deposit_text`, `key_money_text`,
`maintenance_text`, `maintenance_detail`, `other_fees_text`,
`guarantee_initial_text`, `guarantee_monthly_rate`,
`guarantee_monthly_amount_text`, `cleaning_fee_text`,
`support_fee_text`, `key_set_text`, `property_name`, `room_number`

---

## Dependências

```
openpyxl       # Excel
fastapi        # Fase 3 (API)
redis          # Fase 3 (fila)
rq             # Fase 3 (workers)
ollama         # Fase 2 (LLM Vision — instalar via pip ou usar requests)
```

## Instalar dependências mínimas (Fase 1+2)
```bash
pip install openpyxl requests
```
