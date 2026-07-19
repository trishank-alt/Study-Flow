from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.resources.models import Resource


class ResourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, resource: Resource) -> Resource:
        self.db.add(resource)
        await self.db.flush()
        await self.db.refresh(resource)
        return resource

    async def find_all_by_user(self, user_id: int) -> List[Resource]:
        stmt = select(Resource).where(Resource.user_id == user_id).order_by(Resource.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def find_by_id(self, resource_id: int) -> Optional[Resource]:
        stmt = select(Resource).where(Resource.id == resource_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def delete(self, resource: Resource) -> None:
        await self.db.delete(resource)
        await self.db.flush()
