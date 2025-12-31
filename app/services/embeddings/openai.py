import openai
from app.core.config import settings
from app.services.embeddings.base import EmbeddingsProvider
from tenacity import retry, stop_after_attempt, wait_random_exponential

class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
    async def embed_text(self, text: str) -> list[float]:
        text = text.replace("\n", " ")
        response = await self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # OpenAI supports batching, but good to handle token limits. 
        # For simplicity, we just send batch (OpenAI handles lists).
        texts = [t.replace("\n", " ") for t in texts]
        response = await self.client.embeddings.create(input=texts, model=self.model)
        # OpenAI returns list of embeddings, we must ensure order is preserved (it is).
        return [item.embedding for item in response.data]
