from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.settings.service import SettingsService
from app.settings.schemas import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    return await service.get_settings(current_user.id)


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    return await service.update_settings(current_user.id, data)
