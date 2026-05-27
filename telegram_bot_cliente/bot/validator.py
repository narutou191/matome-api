from anthropic import Anthropic
from bot.config import ANTHROPIC_API_KEY

class ClientValidator:
    def __init__(self):
        self.client = Anthropic()
        self.conversation_history = []

    def validate_input(self, user_input: str, block: str) -> dict:
        system_prompt = f"""You are a helpful assistant collecting client information for real estate loans in Japan.
Current block: {block}

For each input:
1. Extract relevant information
2. Normalize data (dates to YYYY/M/D, amounts to integers)
3. Ask clarifying questions if needed
4. Return friendly response in Portuguese (Brazilian Portuguese)

Be conversational and helpful."""

        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return {"text": assistant_message}

    def reset_conversation(self):
        self.conversation_history = []
