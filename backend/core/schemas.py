# backend/core/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserData(BaseModel):
    id: int
    username: str

class SettingsUpdate(BaseModel):
    user_name: str = ""
    weather_city: str
    avatar: Optional[str] = None
    timezone: str = "Europe/Moscow"
    github_token: Optional[str] = None

class ApiKeyAdd(BaseModel):
    provider: str
    api_key: str

class AgentCreateUpdate(BaseModel):
    name: str
    profession: Optional[str] = ""
    description: str = ""
    model: Optional[str] = None
    system_prompt: str = ""
    skills: Dict[str, Any] = {}
    tools: Optional[List[str]] = []
    settings: Optional[Dict[str, Any]] = {}
    is_default: bool = False
    is_main: bool = False
    avatar: Optional[str] = None

class ToolConfirm(BaseModel):
    call_id: str
    approved: bool

class ToolUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    requires_approval: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

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

class TaskToolConfirm(BaseModel):
    tool_call_id: str
    approved: Any

class TaskToolResponse(BaseModel):
    tool_call_id: str
    response_text: str

class FileRW(BaseModel):
    path: str
    content: str = ""
