# backend/core/schemas/agents.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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
