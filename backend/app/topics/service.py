from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.topics.repository import TopicRepository
from app.topics.schemas import TopicCreate, TopicUpdate, TopicResponse
from app.topics.models import DifficultyLevel
from app.shared.exceptions import NotFoundError


class TopicService:
    def __init__(self, db: AsyncSession):
        self.repo = TopicRepository(db)

    async def create_topic(self, subject_id: int, data: TopicCreate) -> TopicResponse:
        if not data.title or not data.title.strip():
            raise ValueError("Topic title cannot be empty")

        # Validate difficulty
        difficulty = data.difficulty.lower()
        if difficulty not in [d.value for d in DifficultyLevel]:
            difficulty = DifficultyLevel.MEDIUM.value

        topic = await self.repo.save(
            subject_id=subject_id,
            title=data.title.strip(),
            difficulty=difficulty,
            estimated_hours=max(0.1, data.estimated_hours),
        )
        return TopicResponse.model_validate(topic)

    async def list_topics(self, subject_id: int) -> List[TopicResponse]:
        topics = await self.repo.find_all_by_subject(subject_id)
        return [TopicResponse.model_validate(t) for t in topics]

    async def update_topic(self, topic_id: int, data: TopicUpdate) -> TopicResponse:
        topic = await self.repo.find_by_id(topic_id)
        if not topic:
            raise NotFoundError("Topic not found")

        update_data = data.model_dump(exclude_unset=True)

        # Clamp completion percentage
        if "completion_percentage" in update_data and update_data["completion_percentage"] is not None:
            update_data["completion_percentage"] = max(0.0, min(100.0, update_data["completion_percentage"]))

        topic = await self.repo.update(topic, **update_data)
        return TopicResponse.model_validate(topic)

    async def delete_topic(self, topic_id: int) -> None:
        topic = await self.repo.find_by_id(topic_id)
        if not topic:
            raise NotFoundError("Topic not found")
        await self.repo.delete(topic)
