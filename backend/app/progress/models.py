from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="study_sessions")
