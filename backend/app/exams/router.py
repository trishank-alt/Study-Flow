from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.exams.service import ExamService
from app.exams.schemas import ExamCreate, ExamResponse

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=List[ExamResponse])
async def list_exams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExamService(db)
    return await service.list_exams(current_user.id)


@router.post("", response_model=ExamResponse, status_code=201)
async def create_exam(
    data: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExamService(db)
    return await service.create_exam(data)


@router.delete("/{exam_id}", status_code=204)
async def delete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExamService(db)
    await service.delete_exam(exam_id)
