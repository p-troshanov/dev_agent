# backend/core/schemas/users.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

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
