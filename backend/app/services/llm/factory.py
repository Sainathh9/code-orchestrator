from app.llm.gemini import GeminiProvider
from app.llm.llm_service import LLMService


class LLMFactory:

    @staticmethod
    def create() -> LLMService:

        provider = GeminiProvider()

        return LLMService(provider)