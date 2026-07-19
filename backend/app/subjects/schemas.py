from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubjectCreate(BaseModel):
    name: str


class SubjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: Optional[datetime] = None
    topic_count: Optional[int] = 0
    completion: Optional[float] = 0.0

    class Config:
        from_attributes = True
