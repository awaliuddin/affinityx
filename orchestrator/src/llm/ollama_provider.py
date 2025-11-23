"""
Ollama local LLM Provider implementation.
"""
import os
from typing import Optional
import httpx
from orchestrator.src.llm.base import BaseLLM, LLMMessage


class OllamaLLM(BaseLLM):
    """Ollama local models provider"""

    def __init__(
        self,
        model: str = "llama2",
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        super().__init__(model, temperature, max_tokens)
        self.api_base = api_base or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Ollama API"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        try:
            response = httpx.post(
                f"{self.api_base}/api/generate",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def generate_with_messages(self, messages: list[LLMMessage]) -> str:
        """Generate response with message history"""
        # Ollama chat API format
        formatted_messages = [m.to_dict() for m in messages]

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        try:
            response = httpx.post(
                f"{self.api_base}/api/chat",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = httpx.get(f"{self.api_base}/api/tags", timeout=5.0)
            return response.status_code == 200
        except:
            return False
