from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from an LLM.
        """
        raise NotImplementedError
