import re
from .base import BaseLLMProvider


def clean_code(text: str) -> str:
    """
    Strips markdown code blocks, backticks, and extra whitespace from generated code.
    """
    if not text:
        return ""
    text = text.strip()
    # Remove leading ```python or ```
    text = re.sub(r"^```[a-zA-Z0-9]*\n", "", text)
    # Remove trailing ```
    text = re.sub(r"\n```$", "", text)
    # Also handle single-line wrapping like `code`
    if text.startswith("`") and text.endswith("`"):
        text = text[1:-1]
    return text.strip()


class LLMService:

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        raw_output = self.provider.generate(prompt)
        return clean_code(raw_output)