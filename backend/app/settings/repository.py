from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.settings.models import UserSettings


class SettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_user_id(self, user_id: int) -> Optional[UserSettings]:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, settings: UserSettings) -> UserSettings:
        self.db.add(settings)
        await self.db.flush()
        await self.db.refresh(settings)
        return settings

    async def update(self, settings: UserSettings, **kwargs) -> UserSettings:
        for key, value in kwargs.items():
            if value is not None:
                setattr(settings, key, value)
        await self.db.flush()
        await self.db.refresh(settings)
        return settings
