from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.topics.models import Topic


class TopicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, subject_id: int, title: str, difficulty: str, estimated_hours: float) -> Topic:
        topic = Topic(
            subject_id=subject_id,
            title=title,
            difficulty=difficulty,
            estimated_hours=estimated_hours,
        )
        self.db.add(topic)
        await self.db.flush()
        await self.db.refresh(topic)
        return topic

    async def find_all_by_subject(self, subject_id: int) -> List[Topic]:
        result = await self.db.execute(
            select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.created_at)
        )
        return list(result.scalars().all())

    async def find_by_id(self, topic_id: int) -> Optional[Topic]:
        result = await self.db.execute(select(Topic).where(Topic.id == topic_id))
        return result.scalar_one_or_none()

    async def update(self, topic: Topic, **kwargs) -> Topic:
        for key, value in kwargs.items():
            if value is not None:
                setattr(topic, key, value)
        await self.db.flush()
        await self.db.refresh(topic)
        return topic

    async def delete(self, topic: Topic) -> None:
        await self.db.delete(topic)
        await self.db.flush()
