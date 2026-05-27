from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ClientValidator:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history = []
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def validate_input(self, user_input: str, block: str) -> dict:
        # Prompts específicos para cada bloco - TOTALMENTE EM PORTUGUÊS
        block_prompts = {
            "personal": """IMPORTANTE: Você está coletando informações PESSOAIS do CLIENTE (não do usuário).

Contexto: Você é um assistente de cadastro para aluguel de imóvel no Japão.
Bloco atual: INFORMAÇÕES PESSOAIS
Dados esperados: nome completo (conforme Zairyu Card), data de nascimento, endereço, CEP, email, telefone, nacionalidade.

Instruções CRÍTICAS:
- Use sempre "o cliente" ou "o(a)" ao se referir à pessoa cadastrada
- NUNCA use "você" ou "seu" ao fazer perguntas sobre os dados
- Faça perguntas assim: "Qual é a data de nascimento do cliente?" NÃO "Qual é sua data de nascimento?"
- Extraia dados relevantes do texto recebido
- Normalize: datas em YYYY/M/D, telefones com formato JP
- Se faltarem detalhes, pergunte especificamente qual informação precisa
- Confirme o que foi coletado
- Responda SEMPRE em português brasileiro, de forma amigável e profissional""",

            "employment": """IMPORTANTE: Você está coletando informações de EMPREGO do CLIENTE (não do usuário).

Contexto: Cadastro para aluguel de imóvel no Japão.
Bloco atual: INFORMAÇÕES DE EMPREGO
Dados esperados: nome da empresa, endereço da empresa, local de trabalho, renda anual, tipo de contrato, data de contratação, dia do pagamento.

Instruções CRÍTICAS:
- Use sempre "o cliente" ou "do cliente" ao se referir à pessoa
- NUNCA use "você" ou "seu"
- Exemplos corretos: "Qual é a renda anual do cliente?" "Qual é o tipo de contrato do cliente?"
- Extraia dados relevantes (nomes, valores, datas)
- Normalize: datas em YYYY/M/D, valores em inteiros sem pontuação
- Se for renda, confirme se é anual ou mensal
- Pergunte sobre tipo de contrato (正社員, 契約社員, etc) se não mencionado
- Responda em português brasileiro, profissional e claro""",

            "family": """IMPORTANTE: Você está coletando informações de FAMÍLIA do CLIENTE (não do usuário).

Contexto: Cadastro para aluguel de imóvel no Japão.
Bloco atual: INFORMAÇÕES FAMILIARES
Dados esperados: estado civil, número de dependentes, nomes e idades dos dependentes.

Instruções CRÍTICAS:
- Use sempre "o cliente", "da cliente", "do cliente" - NUNCA "você" ou "seu"
- Exemplos: "Qual é o estado civil do cliente?" "O cliente tem dependentes?"
- Extraia dados sobre dependentes
- Normalize: idades em números inteiros, datas de nascimento em YYYY/M/D
- Confirme o estado civil (solteiro, casado, divorciado, viúvo)
- Se houver dependentes, pergunte nome e idade de cada um
- Responda em português brasileiro, mantendo tom profissional""",

            "financing": """IMPORTANTE: Você está coletando informações de FINANCIAMENTOS do CLIENTE (não do usuário).

Contexto: Cadastro para aluguel de imóvel no Japão.
Bloco atual: FINANCIAMENTOS E EMPRÉSTIMOS
Dados esperados: se teve liquidações nos últimos 3 meses, número de financiamentos ativos, detalhes.

Instruções CRÍTICAS:
- Use sempre "o cliente", "do cliente" - NUNCA "você" ou "seu"
- Exemplos: "O cliente tem financiamentos ativos?" "Qual foi a liquidação do cliente?"
- Extraia dados sobre empréstimos/financiamentos
- Determine se houve liquidações recentes (últimos 3 meses)
- Para cada financiamento: tipo, instituição, valor, parcelas restantes
- Normalize valores em inteiros
- Responda em português brasileiro, com clareza""",

            "special": """IMPORTANTE: Você está coletando INFORMAÇÕES ESPECIAIS do CLIENTE (não do usuário).

Contexto: Cadastro para aluguel de imóvel no Japão.
Bloco atual: INFORMAÇÕES ESPECIAIS/OBSERVAÇÕES
Dados esperados: trabalho paralelo, licença maternidade, doenças, medicamentos, observações.

Instruções CRÍTICAS:
- Use sempre "o cliente", "da cliente", "do cliente" - NUNCA "você" ou "seu"
- Exemplos: "O cliente tem trabalho paralelo?" "O cliente está em licença maternidade?"
- Extraia informações especiais com discrição
- Mantenha tom respeitoso e profissional
- Se mencionar saúde, apenas confirme sem pedir detalhes invasivos
- Anote qualquer situação especial que afete a candidatura
- Responda em português brasileiro, com total discrição profissional"""
        }

        system_prompt = block_prompts.get(block, block_prompts["personal"])

        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Execute API call in thread pool to avoid blocking
        # With retry logic for rate limits
        loop = asyncio.get_event_loop()

        def call_api_with_retry():
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return self.client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1024,
                        system=system_prompt,
                        messages=self.conversation_history
                    )
                except Exception as e:
                    if "529" in str(e) or "overload" in str(e).lower():
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # 1, 2, 4 seconds
                            time.sleep(wait_time)
                            continue
                    raise

        response = await loop.run_in_executor(self._executor, call_api_with_retry)

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return {"text": assistant_message}

    def reset_conversation(self):
        self.conversation_history = []
