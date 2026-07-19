import os
import httpx
from typing import List, Dict, Optional
from app.ai.providers.provider import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self._call_anthropic(messages, system_prompt)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        # Separate system messages from user/assistant messages
        system_content = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                filtered_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return await self._call_anthropic(filtered_messages, system_content)

    async def _call_anthropic(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key not set. Please set ANTHROPIC_API_KEY in the environment.")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 4000
        }
        if system_prompt:
            payload["system"] = system_prompt
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
