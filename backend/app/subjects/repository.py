from typing import Optional, List
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from app.subjects.models import Subject
from app.topics.models import Topic


class SubjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, user_id: int, name: str) -> Subject:
        subject = Subject(user_id=user_id, name=name)
        self.db.add(subject)
        await self.db.flush()
        await self.db.refresh(subject)
        return subject

    async def find_all_by_user(self, user_id: int) -> List[dict]:
        """Return all subjects for a user, with topic count and avg completion."""
        stmt = (
            select(
                Subject,
                sa_func.count(Topic.id).label("topic_count"),
                sa_func.coalesce(sa_func.avg(Topic.completion_percentage), 0).label("completion"),
            )
            .outerjoin(Topic, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .group_by(Subject.id)
            .order_by(Subject.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.Subject.id,
                "user_id": row.Subject.user_id,
                "name": row.Subject.name,
                "created_at": row.Subject.created_at,
                "topic_count": row.topic_count,
                "completion": round(float(row.completion), 1),
            }
            for row in rows
        ]

    async def find_by_name(self, user_id: int, name: str) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.user_id == user_id, Subject.name == name)
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, subject_id: int) -> Optional[Subject]:
        result = await self.db.execute(select(Subject).where(Subject.id == subject_id))
        return result.scalar_one_or_none()

    async def delete(self, subject: Subject) -> None:
        await self.db.delete(subject)
        await self.db.flush()
