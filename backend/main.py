from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.shared.database import create_tables
from app.shared.logger import logger

# Import all models so SQLAlchemy knows about them
from app.auth.models import User  # noqa: F401
from app.subjects.models import Subject  # noqa: F401
from app.topics.models import Topic  # noqa: F401
from app.exams.models import Exam  # noqa: F401
from app.schedule.models import ScheduleItem  # noqa: F401
from app.progress.models import StudySession  # noqa: F401
from app.settings.models import UserSettings  # noqa: F401
from app.resources.models import Resource  # noqa: F401

# Import routers
from app.auth.router import router as auth_router
from app.subjects.router import router as subjects_router
from app.topics.router import router as topics_router
from app.exams.router import router as exams_router
from app.schedule.router import router as schedule_router
from app.progress.router import router as progress_router
from app.settings.router import router as settings_router
from app.ai.router import router as ai_router
from app.resources.router import router as resources_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Study Planner API...")
    await create_tables()
    logger.info("Database tables created")
    yield
    logger.info("Shutting down Study Planner API...")


app = FastAPI(
    title="Study Planner MVP1",
    description="A modular study planner API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers under /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(subjects_router, prefix="/api")
app.include_router(topics_router, prefix="/api")
app.include_router(exams_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(resources_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
