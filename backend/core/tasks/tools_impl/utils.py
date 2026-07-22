# backend/core/tasks/tools_impl/utils.py
import os
import json
import urllib.request
import urllib.error
import asyncio
import re
from fastapi import HTTPException
from backend.core.config import TOOL_NODE_URL

_default_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../workspace"))
_env_workspace = os.getenv("WORKSPACE_DIR")

if _env_workspace and os.name == 'nt' and _env_workspace.startswith('/'):
    BASE_WORKSPACE = _default_workspace
else:
    BASE_WORKSPACE = _env_workspace or _default_workspace

def _hide_host_path(text: str, user_id: int) -> str:
    if not text:
        return text
    text_str = str(text)
    
    real_base = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}"))
    fake_base = f"/workspace/user_{user_id}"
    
    text_str = text_str.replace('\\\\', '/').replace('\\', '/')
    real_base_forward = real_base.replace('\\', '/')
    
    if real_base_forward in text_str:
        text_str = text_str.replace(real_base_forward, fake_base)
        
    return text_str

def _resolve_path(path: str, work_dir: str, user_id: int) -> str:
    if path:
        path = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff]', '', str(path)).strip()
    if work_dir:
        work_dir = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff]', '', str(work_dir)).strip()
        
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    if not os.path.exists(base_user_dir):
        try: os.makedirs(base_user_dir, exist_ok=True)
        except: pass
        
    norm_base = os.path.normcase(base_user_dir).replace('\\', '/')
    user_dir_marker = f"user_{user_id}"
    
    # 1. Resolve work_dir safely
    safe_work_dir = base_user_dir
    if work_dir:
        cw = work_dir.replace('\\', '/')
        if re.match(r'^[a-zA-Z]:', cw):
            cw = cw.split(':', 1)[1]
        if user_dir_marker in cw:
            cw = cw.split(user_dir_marker, 1)[1]
        cw = cw.lstrip('/')
        safe_work_dir = os.path.abspath(os.path.join(base_user_dir, cw)).replace('\\', '/')
        if not os.path.normcase(safe_work_dir).replace('\\', '/').startswith(norm_base):
            safe_work_dir = base_user_dir

    if not path:
        return safe_work_dir

    # 2. Resolve target path
    cp = path.replace('\\', '/')
    
    if user_dir_marker in cp:
        cp = cp.split(user_dir_marker, 1)[1]
        cp = cp.lstrip('/')
        full_path = os.path.abspath(os.path.join(base_user_dir, cp)).replace('\\', '/')
    else:
        if re.match(r'^[a-zA-Z]:', cp):
            cp = cp.split(':', 1)[1]
            
        if cp.startswith('/'):
            cp = cp.lstrip('/')
            full_path = os.path.abspath(os.path.join(base_user_dir, cp)).replace('\\', '/')
        else:
            full_path = os.path.abspath(os.path.join(safe_work_dir, cp)).replace('\\', '/')

    # 3. Security check
    norm_full = os.path.normcase(full_path).replace('\\', '/')
    if not norm_full.startswith(norm_base):
        return os.path.abspath(os.path.join(base_user_dir, os.path.basename(path))).replace('\\', '/')
        
    return full_path

def _call_tool_node_sync(endpoint: str, payload: dict):
    url = f"{TOOL_NODE_URL}{endpoint}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = resp.read().decode('utf-8')
            return result
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            return f"Ошибка Tool Node ({e.code}): {err_body}"
        except Exception:
            return f"Ошибка Tool Node ({e.code}): {e.reason}"
    except urllib.error.URLError as e:
        return f"Ошибка Tool Node: {e}"
    except Exception as e:
        return f"Критическая ошибка: {str(e)}"

async def _call_tool_node(endpoint: str, payload: dict):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _call_tool_node_sync, endpoint, payload)
