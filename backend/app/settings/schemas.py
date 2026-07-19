from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SettingsResponse(BaseModel):
    user_id: int
    llm_provider: str
    model_name: Optional[str] = None
    ollama_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    model_name: Optional[str] = None
    ollama_url: Optional[str] = None
