import os
from typing import List, Dict, Any, Optional
from app.settings.models import UserSettings
from app.ai.orchestrator import AIOrchestrator
from app.ai.parsers.json_parser import parse_json_markdown
from app.ai.models.chat_response import (
    ExplainResponse,
    QuizResponse,
    ChatHistoryItem,
    ChatResponse,
    ScheduleReviewResponse,
)

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def load_prompt_template(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template {filename} not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class AIService:
    def __init__(self, settings: UserSettings):
        self.settings = settings
        self.provider = AIOrchestrator.get_provider(
            provider_name=settings.llm_provider,
            model_name=settings.model_name,
            ollama_url=settings.ollama_url,
        )

    async def explain_topic(
        self, topic_title: str, subject_name: str, difficulty: str
    ) -> ExplainResponse:
        template = load_prompt_template("tutor.md")
        prompt = template.format(
            topic_title=topic_title,
            subject_name=subject_name,
            difficulty=difficulty,
        )
        response_text = await self.provider.generate(prompt)
        parsed_data = parse_json_markdown(response_text)
        return ExplainResponse(**parsed_data)

    async def generate_quiz(
        self, topic_title: str, subject_name: str, difficulty: str
    ) -> QuizResponse:
        template = load_prompt_template("quiz.md")
        prompt = template.format(
            topic_title=topic_title,
            subject_name=subject_name,
            difficulty=difficulty,
        )
        response_text = await self.provider.generate(prompt)
        parsed_data = parse_json_markdown(response_text)
        return QuizResponse(**parsed_data)

    async def chat_tutor(self, messages: List[ChatHistoryItem]) -> ChatResponse:
        system_prompt = (
            "You are a supportive, high-fidelity AI Academic Tutor. "
            "Help the student understand their topics, explain concepts, "
            "and suggest study strategies. Use clean markdown for formatting."
        )

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        reply = await self.provider.chat(formatted_messages)
        return ChatResponse(reply=reply)

    async def review_schedule(
        self, topics: List[Dict[str, Any]], exams: List[Dict[str, Any]], schedule: List[Dict[str, Any]]
    ) -> ScheduleReviewResponse:
        template = load_prompt_template("advisor.md")

        # Format inputs nicely
        topics_str = "\n".join([
            f"- {t['title']} (Difficulty: {t['difficulty']}, Estimated Hours: {t['estimated_hours']}, Completion: {t['completion_percentage']:.1f}%)"
            for t in topics
        ]) or "No active topics."

        exams_str = "\n".join([
            f"- Exam: {e['name']} on {e['exam_date']} (Subject: {e['subject_name']})"
            for e in exams
        ]) or "No upcoming exams."

        schedule_str = "\n".join([
            f"- {s['scheduled_date']}: Study {s['topic_title']} ({s['subject_name']}) for {s['planned_minutes']} mins (Completed: {s['completed']})"
            for s in schedule
        ]) or "No study schedule generated."

        prompt = template.format(
            topics_data=topics_str,
            exams_data=exams_str,
            schedule_data=schedule_str,
        )
        response_text = await self.provider.generate(prompt)
        parsed_data = parse_json_markdown(response_text)
        return ScheduleReviewResponse(**parsed_data)
