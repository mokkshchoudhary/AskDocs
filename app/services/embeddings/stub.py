import random
from app.services.embeddings.base import EmbeddingsProvider

class StubEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def embed_text(self, text: str) -> list[float]:
        # Deterministic-ish stub: seed with text length
        random.seed(len(text))
        return [random.random() for _ in range(self.dimension)]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed_text(t) for t in texts]
