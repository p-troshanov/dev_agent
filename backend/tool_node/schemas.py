# backend/tool_node/schemas.py
from pydantic import BaseModel

class FileWritePayload(BaseModel):
    path: str
    content: str
    user_id: int

class FileReadPayload(BaseModel):
    path: str
    user_id: int

class CommandPayload(BaseModel):
    command: str
    work_dir: str = ""
    user_id: int

class ServiceStartPayload(BaseModel):
    command: str
    work_dir: str = ""
    user_id: int

class ServiceActionPayload(BaseModel):
    service_id: str
    user_id: int

class ServiceLogsPayload(BaseModel):
    service_id: str
    lines: int = 50
    user_id: int
