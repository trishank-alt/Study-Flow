from datetime import date
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.progress.repository import ProgressRepository
from app.progress.schemas import StudySessionCreate, StudySessionResponse, DashboardStats
from app.subjects.models import Subject
from app.topics.models import Topic
from app.exams.models import Exam


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProgressRepository(db)

    async def log_session(self, data: StudySessionCreate) -> StudySessionResponse:
        session = await self.repo.save_session(data.topic_id, data.duration_minutes)
        return StudySessionResponse.model_validate(session)

    async def get_dashboard(self, user_id: int) -> DashboardStats:
        total_hours = await self.repo.get_total_hours(user_id)
        weekly_hours = await self.repo.get_weekly_hours(user_id)
        streak = await self.repo.get_study_streak(user_id)
        recent = await self.repo.get_recent_sessions(user_id)

        # Count subjects
        subj_result = await self.db.execute(
            select(sa_func.count(Subject.id)).where(Subject.user_id == user_id)
        )
        total_subjects = subj_result.scalar() or 0

        # Count topics
        topic_result = await self.db.execute(
            select(sa_func.count(Topic.id))
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
        )
        total_topics = topic_result.scalar() or 0

        # Overall completion
        comp_result = await self.db.execute(
            select(sa_func.coalesce(sa_func.avg(Topic.completion_percentage), 0))
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
        )
        overall_completion = round(float(comp_result.scalar() or 0), 1)

        # Upcoming exams
        exam_result = await self.db.execute(
            select(sa_func.count(Exam.id))
            .join(Subject, Exam.subject_id == Subject.id)
            .where(Subject.user_id == user_id, Exam.exam_date >= date.today())
        )
        upcoming_exams = exam_result.scalar() or 0

        return DashboardStats(
            total_hours=total_hours,
            weekly_hours=weekly_hours,
            study_streak=streak,
            total_subjects=total_subjects,
            total_topics=total_topics,
            overall_completion=overall_completion,
            upcoming_exams=upcoming_exams,
            recent_sessions=[StudySessionResponse(**s) for s in recent],
        )
