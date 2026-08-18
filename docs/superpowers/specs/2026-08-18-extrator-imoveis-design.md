# Extrator de Imóveis — Web + Telegram Mini App

**Data:** 2026-08-18
**Status:** Design aprovado
**Escopo:** Novo projeto isolado (`extrator-imoveis/`) que extrai dados de 2 capturas de tela de um anúncio de imóvel japonês (DK Portal ou similar) e devolve um resumo de custos formatado com emojis, acessível via widget web standalone e via Telegram (como Mini App).

---

## 1. Contexto e motivação

O usuário (corretor de imóveis no Japão) já tem:
- `vision/` — módulo Python validado (`schema.py` + `normalizer.py`) que converte JSON bruto de LLM em `PropertyData`, com toda a lógica de cálculo (agency_fee = rent×1.1 quando ausente, other_fees = guarantee_monthly + support_fee, parsing de valores em ¥, etc.) já testada contra template real.
- Um MVP em `index.html` + `server.js` (spec: `2026-06-30-vision-mvp-html-design.md`) que já chama a Claude Vision API e formata resultado com emojis, mas só aceita **1 imagem** e não aplica os cálculos derivados (só extrai texto cru).
- `telegram_bot_cliente/` — bot Python separado, para cadastro de clientes (fora de escopo aqui, só referência de padrão/infra).

O pedido: dado o exemplo de 2 capturas de tela (物件概要 + その他詳細), gerar automaticamente o resumo:
```
🏠 アパート 3DK
【月額費用】
💴 家賃: ¥42,000
🚗 駐車場: ¥3,300
🏢 共益費等: ¥3,000
📋 その他費用: ¥3,099
🏘️ 自治会費: ¥600
　　月合計: ¥51,999
【入居時費用】
🔑 礼金: ¥0
🏦 敷金: ¥0
💼 仲介手数料: ¥46,200
🅿️ 駐車場契約: ¥3,300
🧹 クリーニング費: ¥70,000
🛡️ 保証委託料: ¥22,000
🗝️ 鍵セット費: ¥3,300
　　入居時合計: ¥144,800
━━━━━━━━━━━━━━━
💰 合計金額: ¥196,799
━━━━━━━━━━━━━━━
```
Esses valores já batem exatamente com a lógica existente em `vision/normalizer.py` (verificado manualmente: 1,119 + 1,980 = 3,099 para その他費用; 42,000 × 1.1 = 46,200 para 仲介手数料). Portanto essa lógica é **reaproveitada por importação**, não reescrita.

Requisito adicional descoberto durante o design: o Telegram recomprime fotos enviadas como "Foto" (redimensiona, reduz qualidade JPEG), degradando a extração de texto pequeno. Em vez de pedir ao usuário para enviar como "Arquivo/Documento" (passo não-óbvio, fácil de esquecer), a solução escolhida foi abrir o widget web **dentro do Telegram como Mini App** — o upload nunca passa pelo pipeline de compressão de fotos do Telegram, eliminando o problema pela raiz e mantendo a UX simples ("toca no botão, escolhe a imagem, pronto").

---

## 2. Arquitetura

```
extrator-imoveis/
├── core/
│   ├── vision_client.py   # envia as 2 imagens + prompt → Claude Vision API → JSON bruto
│   ├── formatter.py       # PropertyData → texto formatado com emojis
│   └── service.py         # orquestra: imagens → vision_client → normalize() → formatter
├── web/
│   ├── index.html         # upload de 2 imagens; funciona standalone E como Telegram Mini App
│   └── app.py             # FastAPI: serve o HTML + endpoint POST /api/process
├── telegram/
│   └── bot.py             # /start → botão que abre o Mini App (web/index.html hospedado)
├── .env.example
├── requirements.txt
└── README.md
```

`core/service.py` é a única fonte de verdade do fluxo de negócio — tanto `web/app.py` quanto (indiretamente, via Mini App) o Telegram usam exatamente o mesmo caminho, então nunca podem divergir.

`vision.normalizer.normalize()` e `vision.schema.PropertyData` são **importados** do módulo `vision/` já existente na raiz do repo (não duplicados). `extrator-imoveis/` adiciona `vision/` ao `sys.path` (ou o projeto roda a partir da raiz do repo).

### Por que Mini App em vez de bot recebendo fotos diretamente
Um bot Python tradicional (`python-telegram-bot`) recebendo `message.photo` sempre recebe a versão comprimida pelo Telegram — não tem como evitar isso no lado do bot. A única forma de pular essa compressão é o usuário nunca enviar a imagem *como mensagem de chat*. Um Telegram Mini App (WebView com upload HTTP normal) resolve isso: a imagem vai direto do dispositivo do usuário pro servidor via `multipart/form-data`, igual um upload de site comum.

**Trade-off aceito:** Telegram Mini Apps exigem uma URL HTTPS pública — não dá pra rodar só localhost. O repo já tem `render.yaml` (padrão de hospedagem já usado em outros projetos), então `web/app.py` será hospedado lá.

---

## 3. Fluxo de dados

1. Usuário abre o widget (direto no navegador, ou via botão do bot do Telegram que abre o Mini App) e faz upload das 2 capturas de tela (物件概要 + その他詳細)
2. `web/app.py` recebe as 2 imagens em `POST /api/process` e chama `core/service.py`
3. `core/service.py`:
   a. `vision_client.extract(imagens)` — **1 chamada** à Claude Vision API com as 2 imagens na mesma mensagem, pedindo o JSON já documentado no `CLAUDE.md` (`rent_text`, `parking_text`, `maintenance_detail`, `guarantee_monthly_amount_text`, `agency_fee_text`, etc.)
   b. `vision.normalizer.normalize(raw)` → `PropertyData` (calcula agency_fee, other_fees, community_fee, totais)
   c. `formatter.format_emoji(PropertyData)` → texto final
4. `web/app.py` devolve o texto como JSON `{ "result": "..." }`
5. Frontend mostra o texto formatado na tela com botão "📋 Copiar"

### Contrato do JSON bruto (prompt da Claude Vision API)
Reaproveita o contrato já documentado no `CLAUDE.md` do projeto VISION:
```
property_name, room_number, customer_name, move_in_date, rent_start_date,
rent_text, parking_text, deposit_text, key_money_text,
maintenance_text, maintenance_detail, other_fees_text,
guarantee_initial_text, guarantee_monthly_rate, guarantee_monthly_amount_text,
cleaning_fee_text, support_fee_text, key_set_text, agency_fee_text
```
O prompt instrui a Claude a olhar as 2 imagens juntas e preencher esse único JSON (dados de uma imagem complementam a outra).

### Mapeamento campo → emoji (saída)
Igual ao já definido em `2026-06-30-vision-mvp-html-design.md`, com os campos derivados calculados por `normalize()`:

| Campo (PropertyData) | Emoji | Label | Seção |
|---|---|---|---|
| rent | 💴 | 家賃 | Mensal |
| parking | 🚗 | 駐車場 | Mensal |
| maintenance | 🏢 | 共益費等 | Mensal |
| other_fees | 📋 | その他費用 | Mensal |
| community_fee | 🏘️ | 自治会費 | Mensal |
| (soma mensal) | — | 月合計 | Mensal |
| key_money | 🔑 | 礼金 | Entrada |
| deposit | 🏦 | 敷金 | Entrada |
| agency_fee | 💼 | 仲介手数料 | Entrada |
| parking_contract_fee | 🅿️ | 駐車場契約 | Entrada |
| cleaning_fee | 🧹 | クリーニング費 | Entrada |
| guarantee_initial | 🛡️ | 保証委託料 | Entrada |
| key_set_fee | 🗝️ | 鍵セット費 | Entrada |
| (soma entrada) | — | 入居時合計 | Entrada |
| (soma geral) | 💰 | 合計金額 | Total |

Além disso, o texto final inclui o aviso padrão já usado pelo usuário:
> ⚠️ Observação: estes valores são apenas uma referência inicial e podem variar. A confirmação oficial dos valores ocorre somente na etapa de intenção de contrato.
> 📷 A precisão dos valores depende da qualidade da imagem. Para melhores resultados, prefira capturas de tela direto do portal.

---

## 4. Componentes

**`core/vision_client.py`**
- Função `extract(images: list[bytes]) -> dict` — monta a mensagem com as 2 imagens em base64 + prompt, chama `POST https://api.anthropic.com/v1/messages`, faz parse do JSON da resposta (mesmo padrão de extração via regex já usado em `server.js`, adaptado pra Python).
- Erros da API (401, 429, timeout, resposta sem JSON) sobem como exceções tipadas, tratadas na camada web.

**`core/formatter.py`**
- Função `format_emoji(prop: PropertyData) -> str` — monta o texto final conforme a tabela acima, incluindo os totais (月合計, 入居時合計, 合計金額) e o aviso padrão.

**`core/service.py`**
- Função `process_property(images: list[bytes]) -> str` — orquestra vision_client → normalizer.normalize → formatter, ponto único de entrada usado pela camada web.

**`web/app.py`** (FastAPI)
- Serve `index.html` na raiz
- `POST /api/process` — recebe 2 imagens (multipart), chama `core.service.process_property`, devolve `{ "result": "..." }` ou erro
- Lê `ANTHROPIC_API_KEY` do `.env` do servidor (nunca exposta ao navegador)

**`web/index.html`**
- Upload de 2 imagens (drag-drop ou seleção), preview, botão "Processar"
- Detecta se está rodando dentro do Telegram (`window.Telegram?.WebApp`) pra ajustar tema/comportamento, mas funciona igual fora dele
- Mostra resultado com botão "📋 Copiar"

**`telegram/bot.py`** (novo bot, token próprio via BotFather)
- `/start` → mensagem de boas-vindas + botão inline do tipo Web App apontando para a URL pública de `web/index.html`
- Não processa fotos diretamente — todo o trabalho pesado acontece dentro do Mini App

---

## 5. Tratamento de erros

| Erro | Onde | Mensagem |
|---|---|---|
| Imagem em formato inválido | web | ❌ Formato inválido. Use PNG, JPG ou WebP |
| Menos de 2 imagens enviadas | web | ❌ Envie as 2 capturas de tela (物件概要 e その他詳細) |
| Falha de autenticação na Claude API | web | ❌ Erro de configuração do servidor. Avise o administrador |
| Rate limit da Claude API | web | ⚠️ Limite de requisições atingido. Aguarde um momento |
| Timeout (>30s) | web | ❌ Demorou muito. Tente novamente |
| JSON não-parseável na resposta da Claude | web | ❌ Não consegui extrair dados dessas imagens. Tente capturas mais nítidas |

Como a API key mora no servidor, o usuário nunca vê erros de "chave inválida" — esses ficam só nos logs do servidor.

---

## 6. Testes

- **Unitário (`formatter`):** dado um `PropertyData` fixo, o texto gerado bate byte-a-byte com o formato esperado (incluindo separadores e aviso final).
- **Unitário (`service`, com `vision_client` mockado):** dado um JSON bruto fixo (o exemplo real do usuário: rent=42000, guarantee_monthly=1119, support=1980, other_fees_text="町内会費 600円"...), o texto final bate exatamente com o resultado esperado (¥51,999 mensal / ¥144,800 entrada / ¥196,799 total).
- **Manual (calibração):** rodar o fluxo completo (upload real das 2 imagens que o usuário mostrou) via `web/index.html` local e conferir visualmente contra o resultado esperado, igual à calibração já feita nos simuladores de financiamento do repo.

---

## 7. Deploy

- `web/app.py` hospedado publicamente (Render, seguindo o padrão do `render.yaml` já usado no repo) — necessário porque Telegram Mini Apps exigem HTTPS público.
- `telegram/bot.py` roda separado (pode ser local/24-7 no mini PC do usuário, como os outros bots do repo) — só precisa de rede pra falar com a API do Telegram e conhecer a URL pública do Mini App.
- `ANTHROPIC_API_KEY` configurada uma vez no `.env` do servidor hospedado.

---

## 8. Fora de escopo (v1)

- Geração de Excel a partir do resultado (o VISION já faz isso separadamente; pode ser integrado depois se necessário)
- Histórico de imóveis processados
- Envio do resultado de volta pro chat do Telegram via `sendData()` — o resultado fica só na tela do Mini App por enquanto, com botão de copiar
- Suporte a mais de 2 imagens por imóvel
