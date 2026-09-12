from .gemini import GeminiProvider
from .llm_service import LLMService


class LLMFactory:

    @staticmethod
    def create(model: str | None = None) -> LLMService:

        provider = GeminiProvider(model=model)

        return LLMService(provider)