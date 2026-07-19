import json
from typing import List, Dict, Optional
from app.ai.providers.provider import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()
        sys_lower = (system_prompt or "").lower()

        # 1. Advisor Prompt (Checked early to avoid overlap with 'schedule')
        if "advisor.md" in prompt_lower or "schedule review" in prompt_lower or "advisor" in prompt_lower:
            return json.dumps({
                "overall_status": "Moderately Balanced",
                "insights": [
                    "You have scheduled daily sessions regularly, which helps build a study habit.",
                    "Your study distribution is clustered around mid-week topics."
                ],
                "warnings": [
                    "Warning: You have scheduled 0 minutes for subjects with upcoming exams next week.",
                    "Warning: Sunday has 9 hours planned, which is prone to burnout."
                ],
                "suggestions": [
                    "Suggestion: Shift 90 minutes of study time from Sunday to Monday and Friday.",
                    "Suggestion: Add a 45-minute practice session specifically for the topic containing exams next Wednesday."
                ]
            })

        # 2. Study Planner Prompt
        elif "schedule" in prompt_lower or "daily study minutes" in prompt_lower:
            return json.dumps({
                "schedule": [
                    {"topic_id": 1, "scheduled_date": "2026-07-20", "planned_minutes": 45},
                    {"topic_id": 1, "scheduled_date": "2026-07-21", "planned_minutes": 45},
                    {"topic_id": 2, "scheduled_date": "2026-07-20", "planned_minutes": 60},
                    {"topic_id": 2, "scheduled_date": "2026-07-22", "planned_minutes": 60}
                ]
            })

        # 3. Tutor Explanation Prompt
        elif "explain" in prompt_lower or "pedagogical" in prompt_lower:
            topic_title = "Selected Topic"
            if "topic title:" in prompt_lower:
                parts = prompt.split("Topic Title:")
                if len(parts) > 1:
                    topic_title = parts[1].split("\n")[0].strip()

            return json.dumps({
                "title": topic_title,
                "overview": f"This is an in-depth pedagogical overview of {topic_title}. It covers the core mechanics, historical context, and foundational theories.",
                "key_points": [
                    "Core Axiom: Understanding the base formulas and assumptions.",
                    "Mechanic Details: How the components interact with each other.",
                    "Practical application: Real world uses and execution strategies."
                ],
                "examples": [
                    f"Example 1: Demonstrating {topic_title} with a basic input parameter set.",
                    f"Example 2: A complex, edge-case implementation of {topic_title} showing performance trade-offs."
                ],
                "common_mistakes": [
                    "Confusing the primary variables, which leads to arithmetic errors.",
                    "Neglecting the pre-requisite conditions before applying this model."
                ]
            })

        # 4. Summarizer Prompt
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            return json.dumps({
                "title": "Extracted Notes Summary",
                "summary": "These notes outline the primary concepts, structural layout, and analytical patterns observed. They serve as a roadmap for understanding core system attributes.",
                "key_concepts": [
                    "First Principle: Everything is modular and self-contained.",
                    "Second Principle: State transitions must flow in a single direction."
                ],
                "formulas": [
                    "Rule of Simplicity: Complex Code = Higher Technical Debt",
                    "Efficiency Index: T(n) = O(log n) for search operations"
                ]
            })

        # 5. Exam Extractor Prompt
        elif "exam paper" in prompt_lower or "extractor.md" in prompt_lower or "frequency" in prompt_lower:
            return json.dumps({
                "analyzed_title": "Exam Paper Analysis Report",
                "topics": [
                    {
                        "title": "Dynamic Programming",
                        "frequency": "high",
                        "recommended_hours": 8.0,
                        "insight": "Appeared in 3 out of the last 4 final exam questions. Pay attention to memoization."
                    },
                    {
                        "title": "Red-Black Trees",
                        "frequency": "medium",
                        "recommended_hours": 4.0,
                        "insight": "Commonly tested as short-answer questions regarding tree rotations."
                    }
                ]
            })

        # 6. Quiz Prompt
        elif "quiz" in prompt_lower or "options" in prompt_lower:
            topic_title = "Selected Topic"
            if "topic:" in prompt_lower:
                parts = prompt.split("Topic:")
                if len(parts) > 1:
                    topic_title = parts[1].split("\n")[0].strip()

            return json.dumps({
                "questions": [
                    {
                        "question": f"Which of the following best describes the core mechanism of {topic_title}?",
                        "options": [
                            "An iterative fallback procedure",
                            "A modular state container optimized for quick lookups",
                            "An external service-based connection layer",
                            "A static database representation"
                        ],
                        "answer_index": 1,
                        "explanation": f"Option B is correct because {topic_title} acts as a modular state container to allow immediate operations."
                    },
                    {
                        "question": f"What is a common pitfall when configuring {topic_title}?",
                        "options": [
                            "Overallocating network sockets",
                            "Hardcoding the dynamic imports",
                            "Neglecting prerequisites and state conditions",
                            "Using lowercase names for identifiers"
                        ],
                        "answer_index": 2,
                        "explanation": "Neglecting prerequisites leads to runtime crashes because the state is not properly aligned."
                    }
                ]
            })


        # Default fallback
        return "I am the AI study planner tutor. Please let me know how I can help you understand your topics!"

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        last_msg = messages[-1]["content"].lower() if messages else ""
        if "hello" in last_msg or "hi" in last_msg:
            return "Hello! I am your AI study tutor. I can explain complex topics, review your schedule, or generate quizzes. What would you like to study today?"
        elif "explain" in last_msg:
            return "I would be happy to explain that! Please click the 'Explain Topic' button on any topic card to see a structured explanation, or tell me the topic title here."
        else:
            return f"That's a great question! Regarding your query, the core concept centers around optimizing study intervals. Let me know if you would like me to detail a specific formula or provide study guidelines!"
