
# pyrefly: ignore-errors
from google import genai
from app.core.config import settings
from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
        )
        return response.text
