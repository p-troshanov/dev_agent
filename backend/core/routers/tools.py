# backend/core/routers/tools.py
import os
import json
import shutil
import re
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.core.database import get_db
from backend.core.schemas import ToolUpdate, FileRW
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/tools", tags=["tools"])

BASE_WORKSPACE = os.getenv("WORKSPACE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../workspace")))

class FileRenameRequest(BaseModel):
    old_path: str
    new_path: str

def _get_safe_user_path(path: str, user_id: int) -> str:
    base_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    os.makedirs(base_dir, exist_ok=True)
    
    if not path:
        return base_dir
        
    clean_path = path.replace('\\', '/')
    if re.match(r'^[a-zA-Z]:', clean_path):
        clean_path = clean_path.split(':', 1)[1]
        
    user_marker = f"user_{user_id}"
    if user_marker in clean_path:
        clean_path = clean_path.split(user_marker, 1)[1]
        
    clean_path = clean_path.lstrip("/")
    full_path = os.path.abspath(os.path.join(base_dir, clean_path)).replace('\\', '/')
    
    norm_base = os.path.normcase(base_dir).replace('\\', '/')
    norm_full = os.path.normcase(full_path).replace('\\', '/')
    
    if not norm_full.startswith(norm_base):
        raise HTTPException(status_code=403, detail="Доступ запрещен: выход за пределы песочницы.")
        
    return full_path

@router.get("")
def get_tools(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id, name, description, category, schema_json, settings, is_active, requires_approval FROM user_tools WHERE user_id = %s ORDER BY category, name ASC', (user_id,))
            res = []
            for r in c.fetchall():
                schema_data = r[4] if r[4] else {}
                settings_data = r[5] if r[5] else {}
                res.append({
                    "id": r[0],
                    "name": r[1],
                    "description": r[2],
                    "category": r[3],
                    "schema_json": schema_data,
                    "settings": settings_data,
                    "is_active": bool(r[6]),
                    "requires_approval": bool(r[7])
                })
            return res

@router.put("/{tool_id}")
def update_tool(tool_id: int, data: ToolUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            update_fields = []
            params = []
            
            if data.description is not None:
                update_fields.append("description = %s")
                params.append(data.description)
                
            if data.category is not None:
                update_fields.append("category = %s")
                params.append(data.category)
                
            if data.is_active is not None:
                update_fields.append("is_active = %s")
                params.append(1 if data.is_active else 0)
                
            if data.requires_approval is not None:
                update_fields.append("requires_approval = %s")
                params.append(1 if data.requires_approval else 0)
                
            if data.settings is not None:
                update_fields.append("settings = %s")
                params.append(json.dumps(data.settings))
                
            if not update_fields:
                return {"status": "ok", "message": "Нет полей для обновления"}
                
            params.append(tool_id)
            params.append(user_id)
            query = f"UPDATE user_tools SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
            
            c.execute(query, tuple(params))
            if c.rowcount == 0:
                raise HTTPException(status_code=404, detail="Tool not found")
            conn.commit()
            return {"status": "ok"}

@router.get("/fs/read")
def local_read_file(path: str, current_user: dict = Depends(get_current_user)):
    safe_path = _get_safe_user_path(path, current_user["id"])
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    with open(safe_path, "r", encoding="utf-8") as f:
        return {"content": f.read()}

@router.post("/fs/write")
def local_write_file(data: FileRW, current_user: dict = Depends(get_current_user)):
    safe_path = _get_safe_user_path(data.path, current_user["id"])
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(data.content)
    return {"status": "ok"}

@router.post("/fs/upload")
async def local_upload_fs(
    file: UploadFile = File(...),
    path: str = Form(default=""),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = current_user["id"]
        if path in ("undefined", "null"):
            path = ""
            
        safe_folder = _get_safe_user_path(path, user_id)
        os.makedirs(safe_folder, exist_ok=True)
        
        filename = os.path.basename(file.filename) if file.filename else "uploaded_file"
        safe_path = os.path.join(safe_folder, filename).replace('\\', '/')
        
        with open(safe_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "ok", "filename": filename}
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fs/list")
def local_list_fs(path: str = "", current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    safe_path = _get_safe_user_path(path, user_id)
    base_dir = _get_safe_user_path("", user_id)
    
    if not os.path.exists(safe_path):
        return {"items": []}
        
    items = []
    if os.path.isdir(safe_path):
        for name in os.listdir(safe_path):
            full_item_path = os.path.join(safe_path, name).replace('\\', '/')
            try:
                rel_to_user = os.path.relpath(full_item_path, base_dir)
                rel_to_user = rel_to_user.replace("\\", "/")
                if rel_to_user == ".":
                    rel_to_user = ""
            except ValueError:
                rel_to_user = full_item_path
                
            items.append({
                "name": name,
                "path": rel_to_user,
                "is_dir": os.path.isdir(full_item_path)
            })
            
    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return {"items": items}

@router.delete("/fs/delete")
def local_delete_fs(path: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    safe_path = _get_safe_user_path(path, user_id)
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Path not found")
    try:
        if os.path.isdir(safe_path):
            shutil.rmtree(safe_path)
        else:
            os.remove(safe_path)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fs/rename")
def local_rename_fs(data: FileRenameRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    safe_old_path = _get_safe_user_path(data.old_path, user_id)
    safe_new_path = _get_safe_user_path(data.new_path, user_id)
    
    if not os.path.exists(safe_old_path):
        raise HTTPException(status_code=404, detail="Путь не найден")
        
    os.makedirs(os.path.dirname(safe_new_path), exist_ok=True)
    
    try:
        os.rename(safe_old_path, safe_new_path)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fs/mkdir")
def local_mkdir_fs(data: FileRW, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    safe_path = _get_safe_user_path(data.path, user_id)
    os.makedirs(safe_path, exist_ok=True)
    return {"status": "ok"}

@router.get("/fs/download")
def local_download_file(path: str, current_user: dict = Depends(get_current_user)):
    safe_path = _get_safe_user_path(path, current_user["id"])
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=safe_path, filename=os.path.basename(safe_path))
