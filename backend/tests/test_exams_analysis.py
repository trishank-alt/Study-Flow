import pytest
import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import BackgroundTasks
from app.shared.database import Base
from app.auth.service import AuthService
from app.auth.schemas import UserCreate
from app.subjects.service import SubjectService
from app.subjects.schemas import SubjectCreate
from app.exams.service import ExamService
from app.exams.schemas import ExamCreate
from app.exams.analysis_service import ExamPaperAnalysisService

# Import all models for Base metadata registration
from app.auth.models import User  # noqa: F401
from app.subjects.models import Subject  # noqa: F401
from app.topics.models import Topic  # noqa: F401
from app.exams.models import Exam  # noqa: F401
from app.schedule.models import ScheduleItem  # noqa: F401
from app.progress.models import StudySession  # noqa: F401
from app.settings.models import UserSettings  # noqa: F401
from app.resources.models import Resource  # noqa: F401


async def setup_test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return engine, Session


def test_exam_paper_analysis_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="examtest@example.com", password="password123"))

            subject_service = SubjectService(db)
            subject = await subject_service.create_subject(user.id, SubjectCreate(name="Algorithms"))

            exam_service = ExamService(db)
            exam = await exam_service.create_exam(ExamCreate(subject_id=subject.id, name="Algorithms Final", exam_date=date.today()))

            analysis_service = ExamPaperAnalysisService(db)
            bg_tasks = BackgroundTasks()

            # Upload paper (mock content)
            resource = await analysis_service.upload_paper(
                user_id=user.id,
                exam_id=exam.id,
                subject_id=subject.id,
                exam_name=exam.name,
                filename="algorithms_final.txt",
                content_type="text/plain",
                file_content=b"Dynamic Programming and Red-Black Trees exam paper text.",
                background_tasks=bg_tasks,
            )

            assert resource.id is not None
            assert resource.resource_type == "EXAM_PAPER"
            assert resource.exam_id == exam.id
            assert resource.embedding_status == "pending"

            # Check status before processing
            status_before = await analysis_service.get_analysis(user.id, exam.id)
            assert status_before["status"] == "processing"
            assert status_before["result"] is None

            # Process AI analysis inline
            await analysis_service.process_exam_paper_ai(resource.id, f"./uploads/{resource.filename}", db=db)

            # Check status after processing
            status_after = await analysis_service.get_analysis(user.id, exam.id)
            assert status_after["status"] == "completed"
            assert status_after["result"] is not None
            assert status_after["result"]["difficulty"] == "hard"
            assert len(status_after["result"]["topics"]) == 2
            assert status_after["result"]["topics"][0]["title"] == "Dynamic Programming"
            assert status_after["result"]["topics"][1]["title"] == "Red-Black Trees"
            assert status_after["result"]["confidence"] == 0.98

            # Clean up analysis
            deleted = await analysis_service.delete_analysis(user.id, exam.id)
            assert deleted is True

            status_deleted = await analysis_service.get_analysis(user.id, exam.id)
            assert status_deleted["status"] == "not_uploaded"

        await engine.dispose()

    asyncio.run(run())
