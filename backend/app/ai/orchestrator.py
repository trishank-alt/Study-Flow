from typing import Optional
from app.ai.providers.provider import BaseLLMProvider
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.anthropic_provider import AnthropicProvider


class AIOrchestrator:
    @staticmethod
    def get_provider(
        provider_name: str,
        model_name: Optional[str] = None,
        ollama_url: Optional[str] = None
    ) -> BaseLLMProvider:
        name = (provider_name or "mock").lower()
        if name == "ollama":
            return OllamaProvider(
                model_name=model_name or "qwen",
                ollama_url=ollama_url or "http://localhost:11434"
            )
        elif name == "openai":
            return OpenAIProvider(model_name=model_name or "gpt-4o-mini")
        elif name == "anthropic":
            return AnthropicProvider(model_name=model_name or "claude-3-5-sonnet-20240620")
        else:
            return MockProvider(model_name=model_name or "mock-model")
