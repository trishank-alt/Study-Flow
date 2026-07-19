from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.shared.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    llm_provider = Column(String(50), default="mock", nullable=False)
    model_name = Column(String(100), default="gpt-4o-mini", nullable=True)
    ollama_url = Column(String(255), default="http://localhost:11434", nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
