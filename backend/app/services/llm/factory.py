from .gemini import GeminiProvider
from .llm_service import LLMService


class LLMFactory:

    @staticmethod
    def create() -> LLMService:

        provider = GeminiProvider()

        return LLMService(provider)