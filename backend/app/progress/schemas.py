from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class StudySessionCreate(BaseModel):
    topic_id: int
    duration_minutes: int


class StudySessionResponse(BaseModel):
    id: int
    topic_id: int
    duration_minutes: int
    completed_at: Optional[datetime] = None
    topic_title: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_hours: float
    weekly_hours: float
    study_streak: int
    total_subjects: int
    total_topics: int
    overall_completion: float
    upcoming_exams: int
    recent_sessions: List[StudySessionResponse] = []
