from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exams.models import Exam
from app.subjects.models import Subject


class ExamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, subject_id: int, name: str, exam_date) -> Exam:
        exam = Exam(subject_id=subject_id, name=name, exam_date=exam_date)
        self.db.add(exam)
        await self.db.flush()
        await self.db.refresh(exam)
        return exam

    async def find_all_by_user(self, user_id: int) -> List[dict]:
        stmt = (
            select(Exam, Subject.name.label("subject_name"))
            .join(Subject, Exam.subject_id == Subject.id)
            .where(Subject.user_id == user_id)
            .order_by(Exam.exam_date)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.Exam.id,
                "subject_id": row.Exam.subject_id,
                "name": row.Exam.name,
                "exam_date": row.Exam.exam_date,
                "subject_name": row.subject_name,
                "created_at": row.Exam.created_at,
            }
            for row in rows
        ]

    async def find_by_id(self, exam_id: int) -> Optional[Exam]:
        result = await self.db.execute(select(Exam).where(Exam.id == exam_id))
        return result.scalar_one_or_none()

    async def delete(self, exam: Exam) -> None:
        await self.db.delete(exam)
        await self.db.flush()
