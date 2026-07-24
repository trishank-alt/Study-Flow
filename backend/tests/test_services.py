import pytest
import asyncio
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.shared.database import Base
from app.auth.service import AuthService
from app.auth.schemas import UserCreate, UserLogin
from app.subjects.service import SubjectService
from app.subjects.schemas import SubjectCreate
from app.topics.service import TopicService
from app.topics.schemas import TopicCreate, TopicUpdate
from app.exams.service import ExamService
from app.exams.schemas import ExamCreate
from app.schedule.service import ScheduleService
from app.schedule.schemas import GenerateScheduleRequest
from app.progress.service import ProgressService
from app.progress.schemas import StudySessionCreate
from app.shared.exceptions import DuplicateError, NotFoundError


async def setup_test_db():
    import os
    db_url = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:"))
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_async_engine(db_url, echo=False, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return engine, Session


def test_auth_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            
            # 1. Register User
            user_in = UserCreate(email="user@example.com", password="password123")
            user = await auth_service.register_user(user_in)
            assert user.id is not None
            assert user.email == "user@example.com"
            
            # 2. Try duplicate registration
            with pytest.raises(DuplicateError):
                await auth_service.register_user(user_in)
                
            # 3. Login User
            login_in = UserLogin(email="user@example.com", password="password123")
            token = await auth_service.login_user(login_in)
            assert token.access_token is not None
        await engine.dispose()
    
    asyncio.run(run())


def test_subjects_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="user2@example.com", password="password123"))
            
            subject_service = SubjectService(db)
            
            # 1. Create Subject
            subj_in = SubjectCreate(name="Computer Science")
            subj = await subject_service.create_subject(user.id, subj_in)
            assert subj.id is not None
            assert subj.name == "Computer Science"
            
            # 2. Duplicate Check
            with pytest.raises(DuplicateError):
                await subject_service.create_subject(user.id, subj_in)
                
            # 3. List Subjects
            subjs = await subject_service.list_subjects(user.id)
            assert len(subjs) == 1
            assert subjs[0].name == "Computer Science"
        await engine.dispose()
        
    asyncio.run(run())


def test_topics_and_progress_flow():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="user3@example.com", password="password123"))
            
            subject_service = SubjectService(db)
            subj = await subject_service.create_subject(user.id, SubjectCreate(name="History"))
            
            topic_service = TopicService(db)
            
            # 1. Create Topic
            topic = await topic_service.create_topic(subj.id, TopicCreate(title="World War I", difficulty="medium", estimated_hours=4.0))
            assert topic.id is not None
            assert topic.title == "World War I"
            
            # 2. Update completion
            updated = await topic_service.update_topic(topic.id, TopicUpdate(completion_percentage=50.0))
            assert updated.completion_percentage == 50.0
            
            # 3. Log a study session
            progress_service = ProgressService(db)
            session = await progress_service.log_session(StudySessionCreate(topic_id=topic.id, duration_minutes=45))
            assert session.id is not None
            assert session.duration_minutes == 45
            
            # 4. Check dashboard
            dashboard = await progress_service.get_dashboard(user.id)
            assert dashboard.total_hours == 0.8
            assert dashboard.weekly_hours == 0.8
            assert dashboard.total_subjects == 1
            assert dashboard.total_topics == 1
        await engine.dispose()
        
    asyncio.run(run())


def test_schedule_generation():
    async def run():
        engine, Session = await setup_test_db()
        async with Session() as db:
            auth_service = AuthService(db)
            user = await auth_service.register_user(UserCreate(email="user4@example.com", password="password123"))
            
            subject_service = SubjectService(db)
            subj = await subject_service.create_subject(user.id, SubjectCreate(name="Biology"))
            
            topic_service = TopicService(db)
            topic = await topic_service.create_topic(subj.id, TopicCreate(title="Genetics", difficulty="hard", estimated_hours=10.0))
            
            exam_service = ExamService(db)
            await exam_service.create_exam(ExamCreate(subject_id=subj.id, name="Biology Final", exam_date=date.today() + timedelta(days=5)))
            
            schedule_service = ScheduleService(db)
            schedule = await schedule_service.generate_schedule(user.id, GenerateScheduleRequest(daily_study_minutes=60))
            
            assert len(schedule) > 0
            assert schedule[0].planned_minutes > 0
            assert schedule[0].topic_title == "Genetics"
        await engine.dispose()
        
    asyncio.run(run())
