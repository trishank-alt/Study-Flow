from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ExamCreate(BaseModel):
    subject_id: int
    name: str
    exam_date: date


class ExamResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    exam_date: date
    subject_name: Optional[str] = None
    created_at: Optional[datetime] = None
    days_remaining: Optional[int] = None

    class Config:
        from_attributes = True
