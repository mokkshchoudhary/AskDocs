from typing import Protocol

class EmbeddingsProvider(Protocol):
    async def embed_text(self, text: str) -> list[float]:
        ...
    
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...
