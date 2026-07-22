# backend/core/routers/agents.py
import json
from fastapi import APIRouter, Depends
from backend.core.database import get_db
from backend.core.schemas import AgentCreateUpdate
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("")
def get_agents(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''SELECT id, name, description, model, system_prompt, skills, tools, is_default, is_main, avatar, profession, settings 
                          FROM agents WHERE user_id = %s OR user_id IS NULL ORDER BY id ASC''', (user_id,))
            res = []
            for r in c.fetchall():
                res.append({
                    "id": r[0], 
                    "name": r[1], 
                    "description": r[2], 
                    "model": r[3],
                    "system_prompt": r[4],
                    "skills": r[5] if r[5] else {}, 
                    "tools": r[6] if r[6] else [],
                    "is_default": bool(r[7]),
                    "is_main": bool(r[8]),
                    "avatar": r[9],
                    "profession": r[10] or "",
                    "settings": r[11] if r[11] else {}
                })
            return res

@router.post("")
def create_agent(data: AgentCreateUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''INSERT INTO agents (user_id, name, profession, description, model, system_prompt, skills, tools, settings, is_default, is_main, avatar)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                      (user_id, data.name, data.profession, data.description, data.model, data.system_prompt, json.dumps(data.skills), json.dumps(data.tools), json.dumps(data.settings), 1 if data.is_default else 0, 1 if data.is_main else 0, data.avatar))
            new_id = c.fetchone()[0]
        conn.commit()
        return {"status": "ok", "id": new_id}

@router.put("/{agent_id}")
def update_agent(agent_id: int, data: AgentCreateUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''UPDATE agents SET name=%s, profession=%s, description=%s, model=%s, system_prompt=%s, skills=%s, tools=%s, settings=%s, is_default=%s, is_main=%s, avatar=%s
                          WHERE id=%s AND user_id=%s''',
                      (data.name, data.profession, data.description, data.model, data.system_prompt, json.dumps(data.skills), json.dumps(data.tools), json.dumps(data.settings), 1 if data.is_default else 0, 1 if data.is_main else 0, data.avatar, agent_id, user_id))
        conn.commit()
        return {"status": "ok"}

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('DELETE FROM agents WHERE id = %s AND user_id = %s', (agent_id, user_id))
        conn.commit()
        return {"status": "ok"}
