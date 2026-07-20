import os
import httpx
from typing import List, Dict, Optional
from app.ai.providers.provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        raw_model = (model_name or "gemini-2.5-flash").strip().lower().replace(" ", "-")
        if "2.5" in raw_model or "3.5" in raw_model:
            normalized = "gemini-2.5-flash"
        elif "2.0" in raw_model:
            normalized = "gemini-2.0-flash"
        elif "pro" in raw_model:
            normalized = "gemini-2.5-pro"
        elif "flash" in raw_model:
            normalized = "gemini-2.5-flash"
        elif raw_model.startswith("gemini-"):
            normalized = raw_model
        else:
            normalized = "gemini-2.5-flash"

        self.model_name = normalized
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise ValueError("Gemini API key not set. Please set GEMINI_API_KEY or GOOGLE_API_KEY in the environment.")

        system_content = None
        contents = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_content = content
            else:
                gemini_role = "user" if role == "user" else "model"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2
            }
        }

        if system_content:
            payload["system_instruction"] = {
                "parts": [{"text": system_content}]
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=600.0)
            if response.is_error:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                raise ValueError(f"Google Gemini API Error ({response.status_code}): {error_msg}")
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini API returned no candidates.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise RuntimeError("Gemini API response contained no text parts.")
            return parts[0].get("text", "")
