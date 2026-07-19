from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from a single prompt."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from chat messages history."""
        pass
