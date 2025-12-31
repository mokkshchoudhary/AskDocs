from typing import Protocol, AsyncGenerator

class LLMProvider(Protocol):
    async def generate_response(self, prompt: str) -> str:
        ...
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        ...
