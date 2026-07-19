from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TopicCreate(BaseModel):
    title: str
    difficulty: str = "medium"
    estimated_hours: float = 1.0


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[float] = None
    completion_percentage: Optional[float] = None


class TopicResponse(BaseModel):
    id: int
    subject_id: int
    title: str
    difficulty: str
    estimated_hours: float
    completion_percentage: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
