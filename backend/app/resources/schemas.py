from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ResourceResponse(BaseModel):
    id: int
    user_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    title: str
    filename: str
    content_type: str
    summary: Optional[str] = None
    embedding_status: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResourceUploadResponse(BaseModel):
    message: str
    resource: ResourceResponse
