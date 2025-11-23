"""
LLM Factory - Creates LLM instances based on configuration.
"""
import os
from typing import Optional
from orchestrator.src.llm.base import BaseLLM, LLMProvider, LLMConfig
from orchestrator.src.llm.openai_provider import OpenAILLM
from orchestrator.src.llm.claude_provider import ClaudeLLM
from orchestrator.src.llm.ollama_provider import OllamaLLM
from orchestrator.src.llm.mock_provider import MockLLM


class LLMFactory:
    """Factory for creating LLM instances"""

    @staticmethod
    def create(config: Optional[LLMConfig] = None) -> BaseLLM:
        """
        Create an LLM instance based on configuration.

        Args:
            config: LLM configuration. If None, uses environment variables.

        Returns:
            BaseLLM instance
        """
        if config is None:
            config = LLMFactory.from_env()

        provider = config.provider

        try:
            if provider == LLMProvider.OPENAI:
                return OpenAILLM(
                    model=config.model,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            elif provider == LLMProvider.CLAUDE:
                return ClaudeLLM(
                    model=config.model,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            elif provider == LLMProvider.OLLAMA:
                return OllamaLLM(
                    model=config.model,
                    api_base=config.api_base,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            elif provider == LLMProvider.MOCK:
                return MockLLM(
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            else:
                raise ValueError(f"Unknown LLM provider: {provider}")
        except (ValueError, ImportError) as e:
            # Fallback to mock if provider fails
            print(f"Warning: Failed to initialize {provider}, falling back to mock: {e}")
            return MockLLM()

    @staticmethod
    def from_env() -> LLMConfig:
        """
        Create LLM configuration from environment variables.

        Environment variables:
            LLM_PROVIDER: openai, claude, ollama, or mock (default: mock)
            LLM_MODEL: Model name (provider-specific default if not set)
            LLM_TEMPERATURE: Temperature for generation (default: 0.7)
            LLM_MAX_TOKENS: Max tokens to generate (default: 2000)
            OPENAI_API_KEY: OpenAI API key
            ANTHROPIC_API_KEY: Anthropic API key
            OLLAMA_API_BASE: Ollama API base URL (default: http://localhost:11434)
        """
        provider_str = os.getenv("LLM_PROVIDER", "mock")
        provider = LLMProvider(provider_str)

        model = os.getenv("LLM_MODEL")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))

        # Get API keys
        api_key = None
        api_base = None

        if provider == LLMProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == LLMProvider.CLAUDE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider == LLMProvider.OLLAMA:
            api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            api_base=api_base,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @staticmethod
    def create_for_agent(agent_type: str) -> BaseLLM:
        """
        Create an LLM instance for a specific agent.

        Supports agent-specific configuration via environment variables:
            ARCHITECT_LLM_PROVIDER, ARCHITECT_LLM_MODEL, etc.

        Args:
            agent_type: Agent type (e.g., "architect", "implementer")

        Returns:
            BaseLLM instance
        """
        prefix = agent_type.upper()

        # Check for agent-specific config
        provider_str = os.getenv(f"{prefix}_LLM_PROVIDER") or os.getenv("LLM_PROVIDER", "mock")
        provider = LLMProvider(provider_str)

        model = os.getenv(f"{prefix}_LLM_MODEL") or os.getenv("LLM_MODEL")
        temperature = float(os.getenv(f"{prefix}_LLM_TEMPERATURE", os.getenv("LLM_TEMPERATURE", "0.7")))
        max_tokens = int(os.getenv(f"{prefix}_LLM_MAX_TOKENS", os.getenv("LLM_MAX_TOKENS", "2000")))

        # Get API keys
        api_key = None
        api_base = None

        if provider == LLMProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == LLMProvider.CLAUDE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider == LLMProvider.OLLAMA:
            api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

        config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            api_base=api_base,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return LLMFactory.create(config)
