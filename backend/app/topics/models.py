from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM, nullable=False)
    estimated_hours = Column(Float, default=1.0, nullable=False)
    completion_percentage = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="topics")
    schedule_items = relationship("ScheduleItem", back_populates="topic", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="topic", cascade="all, delete-orphan")
