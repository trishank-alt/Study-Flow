import httpx
from typing import List, Dict, Optional
from app.ai.providers.provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "qwen", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.ollama_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
