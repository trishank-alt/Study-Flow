import os
from typing import Optional
from datetime import datetime
from pypdf import PdfReader
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.resources.repository import ResourceRepository
from app.resources.models import Resource
from app.settings.service import SettingsService
from app.ai.service import AIService, load_prompt_template
from app.ai.parsers.json_parser import parse_json_markdown
from app.exams.schemas import ExamPaperAnalysisResult


class ExamPaperAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ResourceRepository(db)

    async def upload_paper(
        self,
        user_id: int,
        exam_id: int,
        subject_id: int,
        exam_name: str,
        filename: str,
        content_type: str,
        file_content: bytes,
        background_tasks: BackgroundTasks,
    ) -> Resource:
        UPLOAD_DIR = "./uploads"
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Avoid filename collisions
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # 1. Save file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)

        # 2. Check if a resource already exists for this exam_id and user_id, and delete it
        stmt = select(Resource).where(Resource.exam_id == exam_id, Resource.user_id == user_id)
        res = await self.db.execute(stmt)
        existing_resources = res.scalars().all()
        for old_res in existing_resources:
            old_path = os.path.join(UPLOAD_DIR, old_res.filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
            await self.db.delete(old_res)

        # 3. Create Resource
        resource = Resource(
            user_id=user_id,
            subject_id=subject_id,
            exam_id=exam_id,
            title=f"Past Paper for {exam_name}",
            filename=safe_filename,
            content_type=content_type,
            resource_type="EXAM_PAPER",
            embedding_status="pending",
        )
        self.db.add(resource)
        await self.db.flush()
        await self.db.commit()

        # 4. Schedule background task
        background_tasks.add_task(self.process_exam_paper_ai, resource.id, file_path)

        return resource

    async def get_analysis(self, user_id: int, exam_id: int) -> dict:
        stmt = select(Resource).where(
            Resource.exam_id == exam_id,
            Resource.resource_type == "EXAM_PAPER",
            Resource.user_id == user_id
        )
        res = await self.db.execute(stmt)
        resource = res.scalar_one_or_none()

        if not resource:
            return {"status": "not_uploaded", "result": None, "error": None}

        if resource.embedding_status == "pending":
            return {"status": "processing", "result": None, "error": None}
        elif resource.embedding_status == "failed":
            error_msg = resource.analysis.get("error_message") if isinstance(resource.analysis, dict) else "Extraction failed"
            return {"status": "failed", "result": None, "error": error_msg}
        else:
            return {"status": "completed", "result": resource.analysis, "error": None}

    async def delete_analysis(self, user_id: int, exam_id: int) -> bool:
        stmt = select(Resource).where(
            Resource.exam_id == exam_id,
            Resource.resource_type == "EXAM_PAPER",
            Resource.user_id == user_id
        )
        res = await self.db.execute(stmt)
        resource = res.scalar_one_or_none()
        if not resource:
            return False

        UPLOAD_DIR = "./uploads"
        file_path = os.path.join(UPLOAD_DIR, resource.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        await self.db.delete(resource)
        await self.db.commit()
        return True

    async def process_exam_paper_ai(self, resource_id: int, file_path: str, db: Optional[AsyncSession] = None):
        if db is not None:
            await self._process_exam_paper_ai_with_db(resource_id, file_path, db)
        else:
            from app.shared.database import SessionLocal
            async with SessionLocal() as new_db:
                await self._process_exam_paper_ai_with_db(resource_id, file_path, new_db)

    async def _process_exam_paper_ai_with_db(self, resource_id: int, file_path: str, db: AsyncSession):
        repo = ResourceRepository(db)
        resource = await repo.find_by_id(resource_id)
        if not resource:
            return

        try:
            # 1. Extract Text
            extracted_text = ""
            if resource.content_type == "application/pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            else:  # Fallback as text
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()

            resource.extracted_text = extracted_text or "No readable text found."

            # 2. Call AI to analyze
            settings_service = SettingsService(db)
            settings = await settings_service.get_settings(resource.user_id)

            ai_service = AIService(settings)
            truncated_text = extracted_text[:12000]

            template = load_prompt_template("extractor.md")
            prompt = template.format(text=truncated_text)

            response_text = await ai_service.provider.generate(prompt)
            parsed_data = parse_json_markdown(response_text)

            # 3. Validate parsed_data using Pydantic schema
            validated_result = ExamPaperAnalysisResult(**parsed_data)

            # Store the validated dict directly in the JSON column
            resource.analysis = validated_result.model_dump()
            resource.embedding_status = "processed"
            try:
                from datetime import UTC
                resource.processed_at = datetime.now(UTC)
            except ImportError:
                resource.processed_at = datetime.utcnow()

        except Exception as e:
            resource.embedding_status = "failed"
            # Standard error dictionary structure in JSON column
            resource.analysis = {"error_message": str(e)}

        await repo.save(resource)
        await db.commit()
