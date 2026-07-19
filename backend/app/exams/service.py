from typing import List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.exams.repository import ExamRepository
from app.exams.schemas import ExamCreate, ExamResponse
from app.shared.exceptions import NotFoundError


class ExamService:
    def __init__(self, db: AsyncSession):
        self.repo = ExamRepository(db)

    async def create_exam(self, data: ExamCreate) -> ExamResponse:
        if not data.name or not data.name.strip():
            raise ValueError("Exam name cannot be empty")

        exam = await self.repo.save(data.subject_id, data.name.strip(), data.exam_date)
        return ExamResponse(
            id=exam.id,
            subject_id=exam.subject_id,
            name=exam.name,
            exam_date=exam.exam_date,
            created_at=exam.created_at,
            days_remaining=(exam.exam_date - date.today()).days,
        )

    async def list_exams(self, user_id: int) -> List[ExamResponse]:
        rows = await self.repo.find_all_by_user(user_id)
        result = []
        for row in rows:
            days_remaining = (row["exam_date"] - date.today()).days
            result.append(ExamResponse(**row, days_remaining=days_remaining))
        return result

    async def delete_exam(self, exam_id: int) -> None:
        exam = await self.repo.find_by_id(exam_id)
        if not exam:
            raise NotFoundError("Exam not found")
        await self.repo.delete(exam)
