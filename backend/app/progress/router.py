from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.progress.service import ProgressService
from app.progress.schemas import StudySessionCreate, StudySessionResponse, DashboardStats

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/sessions", response_model=StudySessionResponse, status_code=201)
async def log_session(
    data: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)
    return await service.log_session(data)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressService(db)
    return await service.get_dashboard(current_user.id)
