import openai
from app.core.config import settings
from app.services.llm.base import LLMProvider
from tenacity import retry, stop_after_attempt, wait_random_exponential

class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
    async def generate_response(self, prompt: str) -> str:
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
        )
        return chat_completion.choices[0].message.content

    async def generate_stream(self, prompt: str):
        stream = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
