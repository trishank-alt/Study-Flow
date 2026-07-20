from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.subjects.models import Subject
from app.exams.models import Exam
from app.exams.service import ExamService
from app.exams.analysis_service import ExamPaperAnalysisService
from app.exams.schemas import ExamCreate, ExamResponse, ExamPaperAnalysisResponse

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


@router.post("/{exam_id}/paper", status_code=status.HTTP_202_ACCEPTED)
async def upload_exam_paper(
    exam_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership of the exam
    stmt = (
        select(Exam, Subject.name.label("subject_name"))
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Exam.id == exam_id, Subject.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    row = res.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Exam not found")

    service = ExamPaperAnalysisService(db)
    file_content = await file.read()
    resource = await service.upload_paper(
        user_id=current_user.id,
        exam_id=exam_id,
        subject_id=row.Exam.subject_id,
        exam_name=row.Exam.name,
        filename=file.filename,
        content_type=file.content_type,
        file_content=file_content,
        background_tasks=background_tasks,
    )
    return {
        "message": "Exam paper uploaded successfully. AI analysis has started in the background.",
        "resource_id": resource.id,
        "status": "processing"
    }


@router.get("/{exam_id}/analysis", response_model=ExamPaperAnalysisResponse)
async def get_exam_analysis(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership of the exam
    stmt = (
        select(Exam)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Exam.id == exam_id, Subject.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    exam = res.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    service = ExamPaperAnalysisService(db)
    return await service.get_analysis(current_user.id, exam_id)


@router.delete("/{exam_id}/analysis")
async def delete_exam_analysis(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership of the exam
    stmt = (
        select(Exam)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(Exam.id == exam_id, Subject.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    exam = res.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    service = ExamPaperAnalysisService(db)
    deleted = await service.delete_analysis(current_user.id, exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Exam paper analysis deleted successfully"}
