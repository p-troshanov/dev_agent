# backend/tool_node/utils.py
import os
import shutil
import re
from fastapi import HTTPException
from backend.tool_node.config import BASE_WORKSPACE

def get_safe_path(relative_path: str, user_id: int) -> str:
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    os.makedirs(base_user_dir, exist_ok=True)
    
    if relative_path:
        relative_path = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff]', '', str(relative_path)).strip()
    else:
        relative_path = ""
        
    clean_path = relative_path.replace('\\', '/')
    if re.match(r'^[a-zA-Z]:', clean_path):
        clean_path = clean_path.split(':', 1)[1]
        
    user_dir_marker = f"user_{user_id}"
    if user_dir_marker in clean_path:
        clean_path = clean_path.split(user_dir_marker, 1)[1]
        
    clean_path = clean_path.lstrip("/")
    full_path = os.path.abspath(os.path.join(base_user_dir, clean_path)).replace('\\', '/')
    
    norm_base = os.path.normcase(base_user_dir).replace('\\', '/')
    norm_full = os.path.normcase(full_path).replace('\\', '/')
    
    if not norm_full.startswith(norm_base):
        raise HTTPException(status_code=403, detail="Выход за пределы директории пользователя запрещен.")
        
    return full_path

def build_sandbox_cmd(command: str, cwd: str, base_user_dir: str) -> list:
    bwrap_path = shutil.which("bwrap")
    if not bwrap_path:
        if os.name == 'nt':
            return command
        return ["bash", "-c", command]
        
    return [
        bwrap_path,
        "--ro-bind", "/", "/",
        "--dev", "/dev",
        "--proc", "/proc",
        "--tmpfs", "/workspace",
        "--bind", base_user_dir, base_user_dir,
        "--tmpfs", "/app",
        "--unshare-pid",
        "--chdir", cwd,
        "bash", "-c", command
    ]
