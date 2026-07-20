from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ResourceResponse(BaseModel):
    id: int
    user_id: int
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    exam_id: Optional[int] = None
    title: str
    filename: str
    content_type: str
    resource_type: str
    summary: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    embedding_status: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResourceUploadResponse(BaseModel):
    message: str
    resource: ResourceResponse
