"""
OpenAI LLM Provider implementation.
"""
import os
from typing import Optional
from orchestrator.src.llm.base import BaseLLM, LLMMessage


class OpenAILLM(BaseLLM):
    """OpenAI GPT models provider"""

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        super().__init__(model, temperature, max_tokens)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI API"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    def generate_with_messages(self, messages: list[LLMMessage]) -> str:
        """Generate response with message history"""
        formatted_messages = [m.to_dict() for m in messages]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return bool(self.api_key)
