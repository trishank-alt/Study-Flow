from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


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


class ExamTopicAnalysis(BaseModel):
    title: str
    frequency: str
    recommended_hours: float
    insight: str


class ExamPaperAnalysisResult(BaseModel):
    summary: str
    difficulty: str
    topics: List[ExamTopicAnalysis]
    important_concepts: List[str]
    commonly_repeated: List[str]
    missing_topics: List[str]
    study_strategy: str
    confidence: float


class ExamPaperAnalysisResponse(BaseModel):
    status: str
    result: Optional[ExamPaperAnalysisResult] = None
    error: Optional[str] = None
