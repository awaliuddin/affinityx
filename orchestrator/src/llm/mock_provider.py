"""
Mock LLM Provider for testing without API calls.
"""
from typing import Optional
from orchestrator.src.llm.base import BaseLLM, LLMMessage


class MockLLM(BaseLLM):
    """Mock LLM provider for testing"""

    def __init__(
        self,
        model: str = "mock-model",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        super().__init__(model, temperature, max_tokens)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate mock response"""
        return f"Mock response to: {prompt[:50]}..."

    def generate_with_messages(self, messages: list[LLMMessage]) -> str:
        """Generate mock response with messages"""
        last_message = messages[-1] if messages else None
        if last_message:
            return f"Mock response to: {last_message.content[:50]}..."
        return "Mock response"

    def is_available(self) -> bool:
        """Mock is always available"""
        return True
