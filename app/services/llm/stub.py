import random
from app.services.llm.base import LLMProvider

class StubLLMProvider(LLMProvider):
    async def generate_response(self, prompt: str) -> str:
        return (
            f"**[STUB MODE]**\n\n"
            f"I received your question: '{prompt[:50]}...'\n\n"
            f"However, I am currently running in **Offline Stub Mode** because no `OPENAI_API_KEY` was found in your configuration.\n\n"
            f"To get real answers based on your documents, please:\n"
            f"1. Open your `.env` file.\n"
            f"2. Add `OPENAI_API_KEY=sk-...`\n"
            f"3. Restart the server (`docker-compose restart api worker`)."
        )

    async def generate_stream(self, prompt: str):
        response = f"This is a stub response to: {prompt[:50]}..."
        for word in response.split():
            yield word + " "
