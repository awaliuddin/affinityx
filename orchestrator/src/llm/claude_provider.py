"""
Claude (Anthropic) LLM Provider implementation.
"""
import os
from typing import Optional
from orchestrator.src.llm.base import BaseLLM, LLMMessage


class ClaudeLLM(BaseLLM):
    """Anthropic Claude models provider"""

    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        super().__init__(model, temperature, max_tokens)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Claude API"""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text

    def generate_with_messages(self, messages: list[LLMMessage]) -> str:
        """Generate response with message history"""
        # Extract system message if present
        system_prompt = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                user_messages.append(msg.to_dict())

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": user_messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text

    def is_available(self) -> bool:
        """Check if Claude is available"""
        return bool(self.api_key)
