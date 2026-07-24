from typing import List
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select, cast, Date, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.progress.models import StudySession
from app.topics.models import Topic
from app.subjects.models import Subject


class ProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_session(self, topic_id: int, duration_minutes: int) -> StudySession:
        session = StudySession(topic_id=topic_id, duration_minutes=duration_minutes)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_total_hours(self, user_id: int) -> float:
        stmt = (
            select(sa_func.coalesce(sa_func.sum(StudySession.duration_minutes), 0))
            .join(Topic, StudySession.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        total_minutes = result.scalar() or 0
        return round(total_minutes / 60.0, 1)

    async def get_weekly_hours(self, user_id: int) -> float:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        stmt = (
            select(sa_func.coalesce(sa_func.sum(StudySession.duration_minutes), 0))
            .join(Topic, StudySession.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id, StudySession.completed_at >= week_ago)
        )
        result = await self.db.execute(stmt)
        total_minutes = result.scalar() or 0
        return round(total_minutes / 60.0, 1)

    async def get_study_streak(self, user_id: int) -> int:
        """Count consecutive days with study sessions up to today."""
        is_sqlite = self.db.bind.dialect.name == "sqlite"
        study_date_col = sa_func.date(StudySession.completed_at) if is_sqlite else cast(StudySession.completed_at, Date)
        stmt = (
            select(study_date_col.label("study_date"))
            .join(Topic, StudySession.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .group_by(study_date_col)
            .order_by(study_date_col.desc())
        )
        result = await self.db.execute(stmt)
        dates = [row[0] for row in result.all()]

        if not dates:
            return 0

        streak = 0
        check_date = date.today()
        for d in dates:
            # Handle both date objects and string representations
            if isinstance(d, str):
                from datetime import datetime
                d = datetime.strptime(d, "%Y-%m-%d").date()
            if d == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            elif d < check_date:
                break

        return streak

    async def get_recent_sessions(self, user_id: int, limit: int = 5) -> List[dict]:
        stmt = (
            select(
                StudySession,
                Topic.title.label("topic_title"),
                Subject.name.label("subject_name"),
            )
            .join(Topic, StudySession.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .order_by(StudySession.completed_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.StudySession.id,
                "topic_id": row.StudySession.topic_id,
                "duration_minutes": row.StudySession.duration_minutes,
                "completed_at": row.StudySession.completed_at,
                "topic_title": row.topic_title,
                "subject_name": row.subject_name,
            }
            for row in rows
        ]
