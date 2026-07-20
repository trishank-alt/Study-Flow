from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.topics.models import Topic
from app.subjects.models import Subject
from app.exams.models import Exam
from app.settings.service import SettingsService
from app.ai.service import AIService
from app.schedule.repository import ScheduleRepository
from app.ai.models.chat_response import (
    ExplainResponse,
    QuizResponse,
    ChatRequest,
    ChatResponse,
    ScheduleReviewResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Tutor"])


@router.post("/explain", response_model=ExplainResponse)
async def explain_topic(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topic_id = payload.get("topic_id")
    if not topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required")

    stmt = (
        select(Topic, Subject.name.label("subject_name"))
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Topic.id == topic_id, Subject.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    row = res.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Topic not found")

    settings_service = SettingsService(db)
    settings = await settings_service.get_settings(current_user.id)

    ai_service = AIService(settings)
    return await ai_service.explain_topic(
        topic_title=row.Topic.title,
        subject_name=row.subject_name,
        difficulty=row.Topic.difficulty,
    )


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topic_id = payload.get("topic_id")
    if not topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required")

    stmt = (
        select(Topic, Subject.name.label("subject_name"))
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Topic.id == topic_id, Subject.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    row = res.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Topic not found")

    settings_service = SettingsService(db)
    settings = await settings_service.get_settings(current_user.id)

    ai_service = AIService(settings)
    return await ai_service.generate_quiz(
        topic_title=row.Topic.title,
        subject_name=row.subject_name,
        difficulty=row.Topic.difficulty,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_tutor(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings_service = SettingsService(db)
    settings = await settings_service.get_settings(current_user.id)

    ai_service = AIService(settings)
    try:
        return await ai_service.chat_tutor(payload.messages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/review-schedule", response_model=ScheduleReviewResponse)
async def review_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Fetch incomplete topics
    topic_stmt = (
        select(Topic, Subject.name.label("subject_name"))
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id, Topic.completion_percentage < 100)
    )
    topic_res = await db.execute(topic_stmt)
    topic_rows = topic_res.all()
    topics = [
        {
            "title": row.Topic.title,
            "difficulty": row.Topic.difficulty,
            "estimated_hours": row.Topic.estimated_hours,
            "completion_percentage": row.Topic.completion_percentage,
            "subject_name": row.subject_name,
        }
        for row in topic_rows
    ]

    # 2. Fetch upcoming exams
    exam_stmt = (
        select(Exam, Subject.name.label("subject_name"))
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id)
    )
    exam_res = await db.execute(exam_stmt)
    exam_rows = exam_res.all()
    exams = [
        {
            "name": row.Exam.name,
            "exam_date": str(row.Exam.exam_date),
            "subject_name": row.subject_name,
        }
        for row in exam_rows
    ]

    # 3. Fetch schedule items
    schedule_repo = ScheduleRepository(db)
    schedule = await schedule_repo.find_all_by_user(current_user.id)

    settings_service = SettingsService(db)
    settings = await settings_service.get_settings(current_user.id)

    ai_service = AIService(settings)
    return await ai_service.review_schedule(topics, exams, schedule)
