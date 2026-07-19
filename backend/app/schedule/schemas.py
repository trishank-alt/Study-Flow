from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ScheduleItemCreate(BaseModel):
    topic_id: int
    scheduled_date: date
    planned_minutes: int = 60


class ScheduleItemUpdate(BaseModel):
    completed: Optional[bool] = None


class ScheduleItemResponse(BaseModel):
    id: int
    topic_id: int
    scheduled_date: date
    planned_minutes: int
    completed: bool
    topic_title: Optional[str] = None
    subject_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenerateScheduleRequest(BaseModel):
    """Request to generate a study schedule leading up to exams."""
    daily_study_minutes: int = 120
    start_date: Optional[date] = None
