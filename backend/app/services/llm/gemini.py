
# pyrefly: ignore-errors
from google import genai
from app.core.config import settings
from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self, model: str | None = None):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model = model or settings.MODEL_NAME

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text
