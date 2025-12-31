from app.core.config import settings
from app.services.embeddings.base import EmbeddingsProvider
from app.services.embeddings.stub import StubEmbeddingsProvider
from app.services.embeddings.openai import OpenAIEmbeddingsProvider

def get_embeddings_provider() -> EmbeddingsProvider:
    if settings.USE_LOCAL_LLM_STUB or not settings.OPENAI_API_KEY:
        return StubEmbeddingsProvider()
    return OpenAIEmbeddingsProvider()
