from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.topics.service import TopicService
from app.topics.schemas import TopicCreate, TopicUpdate, TopicResponse

router = APIRouter(tags=["Topics"])


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicResponse])
async def list_topics(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TopicService(db)
    return await service.list_topics(subject_id)


@router.post("/subjects/{subject_id}/topics", response_model=TopicResponse, status_code=201)
async def create_topic(
    subject_id: int,
    data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TopicService(db)
    return await service.create_topic(subject_id, data)


@router.patch("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TopicService(db)
    return await service.update_topic(topic_id, data)


@router.delete("/topics/{topic_id}", status_code=204)
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TopicService(db)
    await service.delete_topic(topic_id)
