from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.subjects.service import SubjectService
from app.subjects.schemas import SubjectCreate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubjectService(db)
    return await service.list_subjects(current_user.id)


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(
    data: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubjectService(db)
    return await service.create_subject(current_user.id, data)


@router.delete("/{subject_id}", status_code=204)
async def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SubjectService(db)
    await service.delete_subject(current_user.id, subject_id)
