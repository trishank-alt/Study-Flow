from typing import List
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schedule.repository import ScheduleRepository
from app.schedule.schemas import (
    ScheduleItemResponse,
    ScheduleItemUpdate,
    GenerateScheduleRequest,
)
from app.topics.models import Topic, DifficultyLevel
from app.subjects.models import Subject
from app.exams.models import Exam
from app.shared.exceptions import NotFoundError


# Difficulty weights for scheduling priority
DIFFICULTY_WEIGHTS = {
    DifficultyLevel.HARD: 3,
    DifficultyLevel.MEDIUM: 2,
    DifficultyLevel.EASY: 1,
}


class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ScheduleRepository(db)

    async def list_schedule(self, user_id: int) -> List[ScheduleItemResponse]:
        rows = await self.repo.find_all_by_user(user_id)
        return [ScheduleItemResponse(**row) for row in rows]

    async def update_item(self, item_id: int, data: ScheduleItemUpdate) -> ScheduleItemResponse:
        item = await self.repo.find_by_id(item_id)
        if not item:
            raise NotFoundError("Schedule item not found")
        update_data = data.model_dump(exclude_unset=True)
        item = await self.repo.update(item, **update_data)
        return ScheduleItemResponse.model_validate(item)

    async def generate_schedule(
        self, user_id: int, request: GenerateScheduleRequest
    ) -> List[ScheduleItemResponse]:
        """
        AI or Rule-based schedule generation:
        1. Fetch user's settings to check provider.
        2. Get all topics with < 100% completion for the user.
        3. Get upcoming exams.
        4. If AI provider is active, try to plan with AI.
        5. Fallback to rule-based distribution.
        """
        start = request.start_date or date.today()
        daily_minutes = request.daily_study_minutes

        # Get settings
        from app.settings.service import SettingsService
        settings_service = SettingsService(self.db)
        settings = await settings_service.get_settings(user_id)

        # Fetch all incomplete topics for the user
        topic_stmt = (
            select(Topic, Subject.name.label("subject_name"))
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Subject.user_id == user_id, Topic.completion_percentage < 100)
        )
        topic_result = await self.db.execute(topic_stmt)
        topic_rows = topic_result.all()

        if not topic_rows:
            await self.repo.delete_all_by_user(user_id)
            return []

        # Fetch upcoming exams
        exam_stmt = (
            select(Exam, Subject.name.label("subject_name"))
            .join(Subject, Exam.subject_id == Subject.id)
            .where(Subject.user_id == user_id, Exam.exam_date >= start)
            .order_by(Exam.exam_date)
        )
        exam_result = await self.db.execute(exam_stmt)
        exam_rows = exam_result.all()
        exams = [row.Exam for row in exam_rows]

        # Determine whether to use AI or rule-based generation
        should_use_ai = request.use_ai if request.use_ai is not None else (settings.llm_provider != "rule-based")

        if should_use_ai:
            try:
                from app.ai.service import AIService, load_prompt_template
                from app.ai.parsers.json_parser import parse_json_markdown
                from app.ai.models.planning_response import PlanningResponse
                from app.ai.providers.mock_provider import MockProvider
                from app.shared.logger import logger

                if settings.llm_provider == "rule-based":
                    provider_to_use = MockProvider()
                    logger.info("AI schedule requested while settings is rule-based; using MockProvider.")
                else:
                    ai_service = AIService(settings)
                    provider_to_use = ai_service.provider

                logger.info(f"Generating schedule with AI provider: {provider_to_use.__class__.__name__}")

                topics_str = "\n".join([
                    f"- Topic ID {row.Topic.id}: {row.Topic.title} (Subject: {row.subject_name}, Difficulty: {row.Topic.difficulty}, Remaining Estimated Hours: {row.Topic.estimated_hours * (1.0 - row.Topic.completion_percentage / 100.0):.1f}h)"
                    for row in topic_rows
                ])

                exams_str = "\n".join([
                    f"- Exam: {row.Exam.name} on {row.Exam.exam_date} (Subject: {row.subject_name})"
                    for row in exam_rows
                ])

                template = load_prompt_template("planner.md")
                prompt = template.format(
                    daily_study_minutes=daily_minutes,
                    start_date=start,
                    topics_data=topics_str or "No incomplete topics.",
                    exams_data=exams_str or "No upcoming exams.",
                )

                response_text = await provider_to_use.generate(prompt)
                parsed = parse_json_markdown(response_text)
                planning_res = PlanningResponse(**parsed)

                valid_topic_ids = {row.Topic.id for row in topic_rows}
                topic_id_list = [row.Topic.id for row in topic_rows]

                items_to_save = []
                for idx, item in enumerate(planning_res.schedule):
                    target_topic_id = item.topic_id if item.topic_id in valid_topic_ids else topic_id_list[idx % len(topic_id_list)]
                    items_to_save.append({
                        "topic_id": target_topic_id,
                        "scheduled_date": item.scheduled_date,
                        "planned_minutes": max(item.planned_minutes, 15),
                    })

                if items_to_save:
                    await self.repo.delete_all_by_user(user_id)
                    await self.repo.save_bulk(items_to_save)
                    await self.db.flush()
                    return await self.list_schedule(user_id)

            except Exception as e:
                from app.shared.logger import logger
                logger.warning(f"AI schedule generation failed, falling back to rule-based schedule. Error: {str(e)}")

        # Clear existing schedule for rule-based generation / fallback
        await self.repo.delete_all_by_user(user_id)

        # Determine the scheduling horizon
        if exams:
            end_date = max(e.exam_date for e in exams)
        else:
            end_date = start + timedelta(days=14)  # Default 2 weeks

        total_days = max((end_date - start).days, 1)

        # Score each topic by priority
        scored_topics = []
        for row in topic_rows:
            topic = row.Topic
            remaining = 100.0 - topic.completion_percentage
            difficulty_weight = DIFFICULTY_WEIGHTS.get(
                DifficultyLevel(topic.difficulty), 2
            )
            # Remaining hours needed
            remaining_hours = topic.estimated_hours * (remaining / 100.0)
            score = remaining_hours * difficulty_weight
            scored_topics.append({
                "topic": topic,
                "subject_name": row.subject_name,
                "remaining_hours": remaining_hours,
                "score": score,
            })

        # Sort by score descending (highest priority first)
        scored_topics.sort(key=lambda x: x["score"], reverse=True)

        # Distribute across days
        total_score = sum(t["score"] for t in scored_topics)
        if total_score == 0:
            return []

        schedule_items = []
        current_date = start

        for day_offset in range(total_days):
            current_date = start + timedelta(days=day_offset)
            remaining_minutes = daily_minutes

            for st in scored_topics:
                if remaining_minutes <= 0:
                    break
                if st["remaining_hours"] <= 0:
                    continue

                # Allocate proportional time
                proportion = st["score"] / total_score
                minutes_for_topic = min(
                    int(daily_minutes * proportion),
                    remaining_minutes,
                    int(st["remaining_hours"] * 60),
                )
                minutes_for_topic = max(minutes_for_topic, 15)  # minimum 15 min block

                if minutes_for_topic > remaining_minutes:
                    minutes_for_topic = remaining_minutes

                schedule_items.append({
                    "topic_id": st["topic"].id,
                    "scheduled_date": current_date,
                    "planned_minutes": minutes_for_topic,
                })

                remaining_minutes -= minutes_for_topic
                st["remaining_hours"] -= minutes_for_topic / 60.0

        # Bulk save
        if schedule_items:
            await self.repo.save_bulk(schedule_items)

        # Return the generated schedule
        return await self.list_schedule(user_id)
