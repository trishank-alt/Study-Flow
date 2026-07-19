from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.subjects.repository import SubjectRepository
from app.subjects.schemas import SubjectCreate, SubjectResponse
from app.shared.exceptions import DuplicateError, NotFoundError, ForbiddenError


class SubjectService:
    def __init__(self, db: AsyncSession):
        self.repo = SubjectRepository(db)

    async def create_subject(self, user_id: int, data: SubjectCreate) -> SubjectResponse:
        if not data.name or not data.name.strip():
            raise ValueError("Subject name cannot be empty")

        existing = await self.repo.find_by_name(user_id, data.name.strip())
        if existing:
            raise DuplicateError(f"Subject '{data.name}' already exists")

        subject = await self.repo.save(user_id, data.name.strip())
        return SubjectResponse(
            id=subject.id,
            user_id=subject.user_id,
            name=subject.name,
            created_at=subject.created_at,
            topic_count=0,
            completion=0.0,
        )

    async def list_subjects(self, user_id: int) -> List[SubjectResponse]:
        rows = await self.repo.find_all_by_user(user_id)
        return [SubjectResponse(**row) for row in rows]

    async def delete_subject(self, user_id: int, subject_id: int) -> None:
        subject = await self.repo.find_by_id(subject_id)
        if not subject:
            raise NotFoundError("Subject not found")
        if subject.user_id != user_id:
            raise ForbiddenError("You do not own this subject")
        await self.repo.delete(subject)
