from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.shared.dependencies import get_db, get_current_user
from app.auth.models import User
from app.resources.service import ResourceService
from app.resources.schemas import ResourceResponse, ResourceUploadResponse

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("", response_model=ResourceUploadResponse)
async def upload_resource(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    subject_id: Optional[int] = Form(None),
    topic_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    service = ResourceService(db)
    resource = await service.upload_resource(
        user_id=current_user.id,
        title=title,
        filename=file.filename,
        content_type=file.content_type,
        file_content=content,
        subject_id=subject_id,
        topic_id=topic_id,
        background_tasks=background_tasks,
    )
    return ResourceUploadResponse(
        message="Resource uploaded. AI summary generation is in progress in the background.",
        resource=ResourceResponse.model_validate(resource),
    )


@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(db)
    rows = await service.list_resources(current_user.id)
    return [ResourceResponse.model_validate(r) for r in rows]


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(db)
    try:
        await service.delete_resource(resource_id, current_user.id)
        # We need to commit settings deletion
        await db.commit()
        return {"message": "Resource deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
