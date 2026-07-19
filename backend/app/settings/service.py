from sqlalchemy.ext.asyncio import AsyncSession
from app.settings.repository import SettingsRepository
from app.settings.models import UserSettings
from app.settings.schemas import SettingsUpdate


class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SettingsRepository(db)

    async def get_settings(self, user_id: int) -> UserSettings:
        settings = await self.repo.find_by_user_id(user_id)
        if not settings:
            # Lazy initialize settings for the user
            settings = UserSettings(
                user_id=user_id,
                llm_provider="mock",
                model_name="gpt-4o-mini",
                ollama_url="http://localhost:11434"
            )
            settings = await self.repo.save(settings)
        return settings

    async def update_settings(self, user_id: int, data: SettingsUpdate) -> UserSettings:
        settings = await self.get_settings(user_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(settings, **update_data)
