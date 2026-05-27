from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ClientValidator:
    def __init__(self):
        self.client = Anthropic()
        self.conversation_history = []
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def validate_input(self, user_input: str, block: str) -> dict:
        # Prompts específicos para cada bloco
        block_prompts = {
            "personal": """Você está coletando informações PESSOAIS do CLIENTE para aluguel de imóvel no Japão.
Este bloco inclui: nome completo (conforme Zairyu Card), data de nascimento, endereço, CEP, email, telefone, nacionalidade.

Para a informação recebida:
1. Extraia dados relevantes
2. Normalize: datas em YYYY/M/D, telefones com formato JP
3. Se faltarem detalhes, pergunte especificamente qual informação precisa
4. Confirme o que foi coletado
5. Responda em português brasileiro, de forma amigável e profissional

Próxima pergunta esperada: dados pessoais do cliente""",

            "employment": """Você está coletando informações de EMPREGO do CLIENTE.
Este bloco inclui: nome da empresa, endereço da empresa, local de trabalho, renda anual, tipo de contrato, data de contratação, dia do pagamento.

Para a informação recebida:
1. Extraia dados relevantes (nomes, valores, datas)
2. Normalize: datas em YYYY/M/D, valores em inteiros (sem pontos/vírgulas)
3. Se for renda, confirme se é anual ou mensal
4. Pergunte sobre tipo de contrato (正社員, 契約社員, etc) se não mencionado
5. Responda em português brasileiro, profissional e claro""",

            "family": """Você está coletando informações de FAMÍLIA do CLIENTE.
Este bloco inclui: estado civil, número de dependentes, nomes e idades dos dependentes.

Para a informação recebida:
1. Extraia dados sobre dependentes
2. Normalize: idades em números inteiros, datas de nascimento em YYYY/M/D
3. Confirme o estado civil (solteiro, casado, divorciado, viúvo)
4. Se houver dependentes, pergunte nome e idade de cada um
5. Responda em português, mantendo tom profissional""",

            "financing": """Você está coletando informações sobre FINANCIAMENTOS ATIVOS do CLIENTE.
Este bloco inclui: se teve liquidações nos últimos 3 meses, número de financiamentos ativos, detalhes de cada financiamento.

Para a informação recebida:
1. Extraia dados sobre empréstimos/financiamentos
2. Determine se houve liquidações recentes (últimos 3 meses)
3. Para cada financiamento, colete: tipo, instituição, valor, parcelas restantes
4. Normalize valores em inteiros
5. Responda em português, com clareza""",

            "special": """Você está coletando INFORMAÇÕES ESPECIAIS/NOTAS do CLIENTE.
Este bloco inclui: se tem trabalho paralelo, se está em licença maternidade, se tem doenças, medicamentos, observações especiais.

Para a informação recebida:
1. Extraia informações especiais/sensíveis
2. Mantenha tom respeitoso e profissional
3. Se mencionar saúde, apenas confirme sem pedir detalhes invasivos
4. Anote qualquer situação especial que afete a candidatura
5. Responda em português, com discrição profissional"""
        }

        system_prompt = block_prompts.get(block, block_prompts["personal"])

        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Execute API call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            self._executor,
            lambda: self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=self.conversation_history
            )
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return {"text": assistant_message}

    def reset_conversation(self):
        self.conversation_history = []
