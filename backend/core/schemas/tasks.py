# backend/core/schemas/tasks.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ProjectCreateUpdate(BaseModel):
    name: str
    folder_name: str
    description: Optional[str] = ""
    settings: Optional[Dict[str, Any]] = {}

class TaskCreate(BaseModel):
    title: str
    initial_prompt: str
    agent_id: int
    project_id: int
    work_dir: Optional[str] = ""
    auto_approve_tools: bool = False
    type: Optional[str] = "standard"
    target_action: Optional[str] = "full_execution"

class TaskPhaseUpdate(BaseModel):
    phase: str

class TaskToolConfirm(BaseModel):
    tool_call_id: str
    approved: Any

class TaskToolResponse(BaseModel):
    tool_call_id: str
    response_text: str

class ToolConfirm(BaseModel):
    call_id: str
    approved: bool

class ToolUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    requires_approval: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class FileRW(BaseModel):
    path: str
    content: str = ""
