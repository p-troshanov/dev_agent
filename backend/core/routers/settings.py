# backend/core/routers/settings.py
import json
from fastapi import APIRouter, Depends
from backend.core.database import get_db
from backend.core.schemas import SettingsUpdate
from backend.core.auth import get_current_user
from backend.core.config import DEFAULT_SETTINGS

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("")
def get_settings(current_user: dict = Depends(get_current_user)): 
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT user_name, weather_city, avatar, timezone, github_token FROM user_settings WHERE user_id = %s", (current_user["id"],))
            row = c.fetchone()
            if row:
                return {
                    "user_name": row[0], 
                    "weather_city": row[1], 
                    "avatar": row[2], 
                    "timezone": row[3] or "Europe/Moscow",
                    "github_token": row[4] or ""
                }
    return { **DEFAULT_SETTINGS, "github_token": "" }

@router.post("")
def update_settings(data: SettingsUpdate, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''INSERT INTO user_settings (user_id, user_name, weather_city, avatar, timezone, github_token)
                          VALUES (%s, %s, %s, %s, %s, %s)
                         ON CONFLICT (user_id) DO UPDATE SET user_name = EXCLUDED.user_name, weather_city = EXCLUDED.weather_city, avatar = EXCLUDED.avatar, timezone = EXCLUDED.timezone, github_token = EXCLUDED.github_token''',
                      (current_user["id"], data.user_name, data.weather_city, data.avatar, data.timezone, data.github_token))
        conn.commit()
    return {"status": "ok"}
