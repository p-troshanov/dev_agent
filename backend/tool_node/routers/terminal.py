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
        # Нормализуем путь для Windows (cmd.exe чувствителен к слэшам в cwd)
        cwd = os.path.normpath(cwd)
        
        base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{payload.user_id}"))
        
        cmd = build_sandbox_cmd(payload.command, cwd, base_user_dir)
        is_shell = isinstance(cmd, str)
        
        # --- ЛОГИРОВАНИЕ СТАРТА ---
        print(f"\n[TERMINAL] 🚀 Запуск команды (User ID: {payload.user_id})", flush=True)
        print(f"[TERMINAL] 📁 CWD: {cwd}", flush=True)
        print(f"[TERMINAL] 💻 Исходная команда: {payload.command}", flush=True)
        print(f"[TERMINAL] ⚙️ Итоговая команда: {cmd}", flush=True)
        
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            shell=is_shell, 
            capture_output=True, 
            timeout=60
        )
        
        def decode_output(b: bytes) -> str:
            if not b:
                return ""
            try:
                return b.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return b.decode("cp866")
                except UnicodeDecodeError:
                    return b.decode("cp1251", errors="replace")

        output = decode_output(result.stdout) + decode_output(result.stderr)
        
        # --- ЛОГИРОВАНИЕ РЕЗУЛЬТАТА ---
        print(f"[TERMINAL] 🏁 Код завершения: {result.returncode}", flush=True)
        if output.strip():
            print(f"[TERMINAL] 📄 Вывод:\n{output.strip()[:500]}{'...' if len(output.strip()) > 500 else ''}", flush=True)
        else:
            print(f"[TERMINAL] 📄 Вывод: <пусто>", flush=True)
            
        # Добавляем принудительный статус
        # (чтобы LLM не зависала на пустом выводе от тихих команд, вроде git clone)
        if result.returncode == 0:
            if not output.strip():
                output = "[Успешно (Код 0)]"
            else:
                output += f"\n[Успешно (Код 0)]"
        else:
            output += f"\n[Ошибка (Код {result.returncode})]"
            
        return {
            "status": "ok", 
            "return_code": result.returncode,
            "output": output 
        }
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        print("[TERMINAL] ❌ Ошибка: Превышено время ожидания (60 сек).", flush=True)
        raise HTTPException(status_code=408, detail="Превышено время ожидания (60 сек).")
    except Exception as e:
        print(f"[TERMINAL] ❌ Внутренняя ошибка: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
