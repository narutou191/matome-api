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
