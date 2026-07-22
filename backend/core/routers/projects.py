# backend/core/routers/projects.py
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from backend.core.database import get_db
from backend.core.schemas import ProjectCreateUpdate
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("")
def get_projects(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id, name, description, folder_name, settings, created_at, webhook_token FROM projects WHERE user_id = %s ORDER BY id DESC', (user_id,))
            res = []
            for r in c.fetchall():
                settings_data = r[4] if r[4] else {}
                res.append({
                    "id": r[0],
                    "name": r[1],
                    "description": r[2],
                    "folder_name": r[3],
                    "settings": settings_data,
                    "created_at": r[5],
                    "webhook_token": r[6]
                })
            return res

@router.post("")
def create_project(data: ProjectCreateUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    webhook_token = str(uuid.uuid4())
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''INSERT INTO projects (user_id, name, description, folder_name, settings, webhook_token)
                          VALUES (%s, %s, %s, %s, %s, %s) RETURNING id''',
                      (user_id, data.name, data.description, data.folder_name, json.dumps(data.settings), webhook_token))
            new_id = c.fetchone()[0]
        conn.commit()
    return {"status": "ok", "id": new_id, "webhook_token": webhook_token}

@router.put("/{project_id}")
def update_project(project_id: int, data: ProjectCreateUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''UPDATE projects SET name = %s, description = %s, folder_name = %s, settings = %s
                          WHERE id = %s AND user_id = %s''',
                      (data.name, data.description, data.folder_name, json.dumps(data.settings), project_id, user_id))
            if c.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
        conn.commit()
    return {"status": "ok"}

@router.post("/{project_id}/reset_webhook")
def reset_project_webhook(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    new_token = str(uuid.uuid4())
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('UPDATE projects SET webhook_token = %s WHERE id = %s AND user_id = %s', (new_token, project_id, user_id))
            if c.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
        conn.commit()
    return {"status": "ok", "webhook_token": new_token}

@router.delete("/{project_id}")
def delete_project(project_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE tasks SET project_id = NULL WHERE project_id = %s AND user_id = %s", (project_id, user_id))
            c.execute('DELETE FROM projects WHERE id = %s AND user_id = %s', (project_id, user_id))
            if c.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
        conn.commit()
    return {"status": "ok"}
