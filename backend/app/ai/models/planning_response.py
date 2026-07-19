from pydantic import BaseModel
from datetime import date
from typing import List


class ScheduleItemLLM(BaseModel):
    topic_id: int
    scheduled_date: date
    planned_minutes: int


class PlanningResponse(BaseModel):
    schedule: List[ScheduleItemLLM]
