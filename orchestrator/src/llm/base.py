"""
LLM Provider abstraction layer.
Supports OpenAI, Claude (Anthropic), and local Ollama models.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    MOCK = "mock"  # For testing without API calls


class LLMMessage:
    """Standardized message format across all LLM providers"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class BaseLLM(ABC):
    """Base class for all LLM providers"""

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 2000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def generate_with_messages(self, messages: list[LLMMessage]) -> str:
        """
        Generate a response using a list of messages.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Generated text response
        """
        pass

    def is_available(self) -> bool:
        """Check if the LLM provider is available and configured"""
        return True


class LLMConfig:
    """Configuration for LLM providers"""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.MOCK,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.provider = provider
        self.model = model or self._default_model(provider)
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens

    @staticmethod
    def _default_model(provider: LLMProvider) -> str:
        """Get default model for a provider"""
        defaults = {
            LLMProvider.OPENAI: "gpt-4-turbo-preview",
            LLMProvider.CLAUDE: "claude-3-sonnet-20240229",
            LLMProvider.OLLAMA: "llama2",
            LLMProvider.MOCK: "mock-model",
        }
        return defaults.get(provider, "mock-model")
