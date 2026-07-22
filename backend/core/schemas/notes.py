# backend/core/schemas/notes.py
from pydantic import BaseModel
from typing import Optional

class NoteCategoryCreateUpdate(BaseModel):
    name: str
    color: Optional[str] = "#406894"

class NoteCreateUpdate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None

class NoteScheduleUpdate(BaseModel):
    agent_id: Optional[int] = None
    project_id: Optional[int] = None
    work_dir: str = ""
    auto_approve_tools: bool = True
    cron_period: str = "daily"
    cron_time: str = "12:00"
    is_active: bool = False
