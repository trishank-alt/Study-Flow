from typing import Optional, List
from datetime import date
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.schedule.models import ScheduleItem
from app.topics.models import Topic
from app.subjects.models import Subject


class ScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, topic_id: int, scheduled_date: date, planned_minutes: int) -> ScheduleItem:
        item = ScheduleItem(
            topic_id=topic_id,
            scheduled_date=scheduled_date,
            planned_minutes=planned_minutes,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def save_bulk(self, items: List[dict]) -> List[ScheduleItem]:
        schedule_items = [ScheduleItem(**item) for item in items]
        self.db.add_all(schedule_items)
        await self.db.flush()
        return schedule_items

    async def find_all_by_user(self, user_id: int) -> List[dict]:
        stmt = (
            select(
                ScheduleItem,
                Topic.title.label("topic_title"),
                Subject.name.label("subject_name"),
            )
            .join(Topic, ScheduleItem.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .order_by(ScheduleItem.scheduled_date)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.ScheduleItem.id,
                "topic_id": row.ScheduleItem.topic_id,
                "scheduled_date": row.ScheduleItem.scheduled_date,
                "planned_minutes": row.ScheduleItem.planned_minutes,
                "completed": row.ScheduleItem.completed,
                "topic_title": row.topic_title,
                "subject_name": row.subject_name,
                "created_at": row.ScheduleItem.created_at,
            }
            for row in rows
        ]

    async def find_by_id(self, item_id: int) -> Optional[ScheduleItem]:
        result = await self.db.execute(select(ScheduleItem).where(ScheduleItem.id == item_id))
        return result.scalar_one_or_none()

    async def update(self, item: ScheduleItem, **kwargs) -> ScheduleItem:
        for key, value in kwargs.items():
            if value is not None:
                setattr(item, key, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_all_by_user(self, user_id: int) -> None:
        """Delete all schedule items for a user (used before regeneration)."""
        subquery = (
            select(ScheduleItem.id)
            .join(Topic, ScheduleItem.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
        )
        result = await self.db.execute(subquery)
        ids = [row[0] for row in result.all()]
        if ids:
            await self.db.execute(
                sa_delete(ScheduleItem).where(ScheduleItem.id.in_(ids))
            )
            await self.db.flush()
