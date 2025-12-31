from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.stub import StubLLMProvider
from app.services.llm.openai import OpenAILLMProvider

def get_llm_provider() -> LLMProvider:
    if settings.USE_LOCAL_LLM_STUB or not settings.OPENAI_API_KEY:
        return StubLLMProvider()
    return OpenAILLMProvider()
