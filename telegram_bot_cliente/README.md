# Telegram Bot - Cliente Cadastro

Bot conversacional para coleta de dados de cliente via Telegram, com validação via Claude API e geração automática de Excel.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure .env

Edit `.env` with your API keys:
- `TELEGRAM_BOT_TOKEN`: Get from @BotFather on Telegram
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/

### 3. Run bot

```bash
python -m bot.main
```

## Windows Service (24/7)

```bash
# Install nssm first
choco install nssm

# Install service
python setup_windows_service.py install

# Start
nssm start TelegramClientBot

# Stop
nssm stop TelegramClientBot
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
telegram_bot_cliente/
├── bot/
│   ├── main.py              # Bot entry point
│   ├── handlers.py          # Conversation handlers
│   ├── validator.py         # Claude API integration
│   ├── excel_generator.py   # Excel generation
│   ├── client_data.py       # Data models
│   └── config.py            # Configuration
├── tests/
│   └── test_*.py            # Tests
├── data/
│   └── template.xlsx        # Excel template
├── output/                  # Generated files
└── requirements.txt
```

## Usage

Send `/start` to bot to begin registration.
Send `/complete` when done to generate Excel.
