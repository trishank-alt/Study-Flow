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
from app.topics.service import TopicService
from app.topics.schemas import TopicCreate
from app.settings.service import SettingsService
from app.settings.schemas import SettingsUpdate
from app.ai.service import AIService
from app.resources.service import ResourceService

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
    import os
    db_url = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"))
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return engine, Session


def test_settings_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="settings@example.com", password="password123"))

            settings_service = SettingsService(db)
            # Fetch settings (should lazy initialize)
            settings = await settings_service.get_settings(user.id)
            assert settings.user_id == user.id
            assert settings.llm_provider == "mock"

            # Update settings
            updated = await settings_service.update_settings(user.id, SettingsUpdate(llm_provider="ollama", model_name="llama3"))
            assert updated.llm_provider == "ollama"
            assert updated.model_name == "llama3"

        await engine.dispose()
    asyncio.run(run())


def test_gemini_provider():
    from app.ai.orchestrator import AIOrchestrator
    from app.ai.providers.gemini_provider import GeminiProvider

    provider = AIOrchestrator.get_provider("gemini", model_name="gemini-2.5-flash")
    assert isinstance(provider, GeminiProvider)
    assert provider.model_name == "gemini-2.5-flash"

    # Test key validation error when key is absent
    p_no_key = GeminiProvider(api_key="")
    p_no_key.api_key = None
    with pytest.raises(ValueError, match="Gemini API key not set"):
        asyncio.run(p_no_key.chat([{"role": "user", "content": "hello"}]))



def test_ai_tutor_and_advisor_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="ai@example.com", password="password123"))

            settings_service = SettingsService(db)
            settings = await settings_service.get_settings(user.id)

            ai_service = AIService(settings)

            # Explain topic (mock provider)
            explanation = await ai_service.explain_topic("A* Search", "Artificial Intelligence", "hard")
            assert "A* Search" in explanation.title
            assert len(explanation.key_points) > 0

            # Practice Quiz
            quiz = await ai_service.generate_quiz("A* Search", "Artificial Intelligence", "hard")
            assert len(quiz.questions) > 0
            assert quiz.questions[0].answer_index is not None

            # Advisor review schedule
            review = await ai_service.review_schedule(
                topics=[{"title": "Search", "difficulty": "hard", "estimated_hours": 10.0, "completion_percentage": 10.0}],
                exams=[{"name": "Midterm", "exam_date": "2026-07-25", "subject_name": "AI"}],
                schedule=[{"scheduled_date": "2026-07-20", "topic_title": "Search", "subject_name": "AI", "planned_minutes": 60, "completed": False}]
            )
            assert review.overall_status is not None
            assert len(review.suggestions) > 0

        await engine.dispose()
    asyncio.run(run())


def test_resources_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="res@example.com", password="password123"))

            resource_service = ResourceService(db)
            bg_tasks = BackgroundTasks()

            # Upload a mockup text notes resource
            res = await resource_service.upload_resource(
                user_id=user.id,
                title="Lecture 1 Notes",
                filename="lecture1.txt",
                content_type="text/plain",
                file_content=b"This is the lecture content about Search Algorithms.",
                subject_id=None,
                topic_id=None,
                background_tasks=bg_tasks
            )

            assert res.id is not None
            assert res.title == "Lecture 1 Notes"
            assert res.embedding_status == "pending"

            # Run background task processing inline for test verification
            await resource_service.process_resource_ai(res.id, f"./uploads/{res.filename}", db=db)

            # Retrieve from DB and verify update
            updated_res = await resource_service.get_resource(res.id)
            assert updated_res.embedding_status == "processed"
            assert "Notes" in updated_res.summary

            # List resources
            all_res = await resource_service.list_resources(user.id)
            assert len(all_res) == 1

            # Delete resource
            await resource_service.delete_resource(res.id, user.id)
            deleted = await resource_service.get_resource(res.id)
            assert deleted is None

        await engine.dispose()
    asyncio.run(run())
