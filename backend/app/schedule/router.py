from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.schedule.service import ScheduleService
from app.schedule.schemas import (
    ScheduleItemResponse,
    ScheduleItemUpdate,
    GenerateScheduleRequest,
)

router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("", response_model=List[ScheduleItemResponse])
async def list_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    return await service.list_schedule(current_user.id)


@router.post("/generate", response_model=List[ScheduleItemResponse])
async def generate_schedule(
    request: GenerateScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    return await service.generate_schedule(current_user.id, request)


@router.patch("/{item_id}", response_model=ScheduleItemResponse)
async def update_schedule_item(
    item_id: int,
    data: ScheduleItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ScheduleService(db)
    return await service.update_item(item_id, data)
