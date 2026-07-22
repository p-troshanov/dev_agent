# backend/tool_node/routers/terminal.py
import os
import subprocess
from fastapi import APIRouter, HTTPException
from backend.tool_node.schemas import CommandPayload
from backend.tool_node.utils import get_safe_path, build_sandbox_cmd
from backend.tool_node.config import BASE_WORKSPACE

router = APIRouter(prefix="/api/terminal", tags=["terminal"])

@router.post("/run")
async def run_command(payload: CommandPayload):
    try:
        cwd = get_safe_path(payload.work_dir, payload.user_id) if payload.work_dir else get_safe_path("", payload.user_id)
        base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{payload.user_id}"))
        
        cmd = build_sandbox_cmd(payload.command, cwd, base_user_dir)
        is_shell = isinstance(cmd, str)
        
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            shell=is_shell, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        output = result.stdout + result.stderr
        return {
            "status": "ok", 
            "return_code": result.returncode,
            "output": output 
        }
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Превышено время ожидания выполнения команды (60 сек).")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
