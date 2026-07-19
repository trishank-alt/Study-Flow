from pydantic import BaseModel
from typing import List, Optional


class ExplainResponse(BaseModel):
    title: str
    overview: str
    key_points: List[str]
    examples: List[str]
    common_mistakes: List[str]


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer_index: int
    explanation: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class ChatHistoryItem(BaseModel):
    role: str  # "user" or "assistant" or "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatHistoryItem]
    topic_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str


class ScheduleReviewResponse(BaseModel):
    overall_status: str
    insights: List[str]
    warnings: List[str]
    suggestions: List[str]
