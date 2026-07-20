from typing import Optional
from app.ai.providers.provider import BaseLLMProvider
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.gemini_provider import GeminiProvider


class AIOrchestrator:
    @staticmethod
    def get_provider(
        provider_name: str,
        model_name: Optional[str] = None,
        ollama_url: Optional[str] = None
    ) -> BaseLLMProvider:
        name = (provider_name or "mock").lower()
        if name == "ollama":
            url = ollama_url or "http://127.0.0.1:11434"
            if "localhost" in url:
                url = url.replace("localhost", "127.0.0.1")
            return OllamaProvider(
                model_name=model_name or "qwen",
                ollama_url=url
            )
        elif name == "openai":
            return OpenAIProvider(model_name=model_name or "gpt-4o-mini")
        elif name == "anthropic":
            return AnthropicProvider(model_name=model_name or "claude-3-5-sonnet-20240620")
        elif name in ("gemini", "google"):
            return GeminiProvider(model_name=model_name or "gemini-2.5-flash")
        else:
            return MockProvider(model_name=model_name or "mock-model")
