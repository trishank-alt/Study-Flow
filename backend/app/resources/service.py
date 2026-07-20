import os
from typing import Optional
from datetime import datetime
from fastapi import BackgroundTasks
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from app.resources.models import Resource
from app.resources.repository import ResourceRepository
from app.settings.service import SettingsService
from app.ai.service import AIService, load_prompt_template
from app.ai.parsers.json_parser import parse_json_markdown

UPLOAD_DIR = "./uploads"


class ResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ResourceRepository(db)

    async def list_resources(self, user_id: int):
        return await self.repo.find_all_by_user(user_id)

    async def get_resource(self, resource_id: int):
        return await self.repo.find_by_id(resource_id)

    async def delete_resource(self, resource_id: int, user_id: int):
        resource = await self.repo.find_by_id(resource_id)
        if not resource or resource.user_id != user_id:
            raise ValueError("Resource not found")

        # Remove physical file
        file_path = os.path.join(UPLOAD_DIR, resource.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        await self.repo.delete(resource)
        return True

    async def upload_resource(
        self,
        user_id: int,
        title: str,
        filename: str,
        content_type: str,
        file_content: bytes,
        subject_id: Optional[int],
        topic_id: Optional[int],
        background_tasks: BackgroundTasks,
    ) -> Resource:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Avoid filename collisions by prefixing with timestamp
        timestamp = int(datetime.utcnow().timestamp())
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # 1. Save file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)

        # 2. Save metadata in DB
        resource = Resource(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=topic_id,
            title=title,
            filename=safe_filename,
            content_type=content_type,
            resource_type="NOTE",
            embedding_status="pending",
        )
        resource = await self.repo.save(resource)

        # Commit to save DB immediately
        await self.db.commit()

        # 3. Schedule background processing for text extraction and AI analysis
        background_tasks.add_task(self.process_resource_ai, resource.id, file_path)

        return resource

    async def process_resource_ai(self, resource_id: int, file_path: str, db: Optional[AsyncSession] = None):
        if db is not None:
            await self._process_resource_ai_with_db(resource_id, file_path, db)
        else:
            from app.shared.database import SessionLocal
            async with SessionLocal() as new_db:
                await self._process_resource_ai_with_db(resource_id, file_path, new_db)

    async def _process_resource_ai_with_db(self, resource_id: int, file_path: str, db: AsyncSession):
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

            # 2. Call AI to summarize
            settings_service = SettingsService(db)
            settings = await settings_service.get_settings(resource.user_id)

            ai_service = AIService(settings)
            truncated_text = extracted_text[:12000]

            template = load_prompt_template("summarizer.md")
            prompt = template.format(text=truncated_text)

            response_text = await ai_service.provider.generate(prompt)
            parsed_data = parse_json_markdown(response_text)

            title = parsed_data.get("title", "Summary")
            summary_para = parsed_data.get("summary", "")
            concepts = parsed_data.get("key_concepts", [])
            formulas = parsed_data.get("formulas", [])

            formatted_summary = f"### {title}\n\n{summary_para}\n\n"
            if concepts:
                formatted_summary += "#### Key Concepts\n"
                for c in concepts:
                    formatted_summary += f"- {c}\n"
                formatted_summary += "\n"
            if formulas:
                formatted_summary += "#### Formulas & Core Laws\n"
                for f_item in formulas:
                    formatted_summary += f"- {f_item}\n"

            resource.summary = formatted_summary
            resource.embedding_status = "processed"
            resource.processed_at = datetime.utcnow()

        except Exception as e:
            resource.embedding_status = "failed"
            resource.summary = f"Processing failed: {str(e)}"

        await repo.save(resource)
        await db.commit()

