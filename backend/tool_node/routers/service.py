# backend/tool_node/routers/service.py
import os
import uuid
import subprocess
from fastapi import APIRouter, HTTPException
from backend.tool_node.schemas import ServiceStartPayload, ServiceActionPayload, ServiceLogsPayload
from backend.tool_node.utils import get_safe_path, build_sandbox_cmd
from backend.tool_node.config import BASE_WORKSPACE
from backend.tool_node.state import _bg_services

router = APIRouter(prefix="/api/service", tags=["service"])

@router.post("/start")
async def start_service(payload: ServiceStartPayload):
    try:
        cwd = get_safe_path(payload.work_dir, payload.user_id) if payload.work_dir else get_safe_path("", payload.user_id)
        base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{payload.user_id}"))
        service_id = f"{payload.user_id}_{str(uuid.uuid4())[:8]}"
        log_file_path = os.path.join(cwd, f".service_{service_id}.log")
        
        cmd = build_sandbox_cmd(payload.command, cwd, base_user_dir)
        is_shell = isinstance(cmd, str)
        
        log_f = open(log_file_path, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=cwd, shell=is_shell, stdout=log_f, stderr=subprocess.STDOUT)
        
        _bg_services[service_id] = {"process": proc, "log_file": log_file_path, "command": payload.command}
        return {"output": f"✅ Фоновый процесс запущен.\nID сервиса: {service_id}\nPID: {proc.pid}\nЛоги пишутся в: {log_file_path}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_service(payload: ServiceActionPayload):
    if not payload.service_id.startswith(f"{payload.user_id}_"):
        raise HTTPException(status_code=403, detail="Доступ запрещен.")
    if payload.service_id in _bg_services:
        proc = _bg_services[payload.service_id]["process"]
        proc.terminate()
        return {"output": f"✅ Сигнал terminate отправлен процессу {payload.service_id} (PID {proc.pid})."}
    return {"output": f"ОШИБКА: Сервис {payload.service_id} не найден."}

@router.post("/status")
async def status_service(payload: ServiceActionPayload):
    if payload.service_id:
        if not payload.service_id.startswith(f"{payload.user_id}_"):
            raise HTTPException(status_code=403, detail="Доступ запрещен.")
        if payload.service_id in _bg_services:
            proc = _bg_services[payload.service_id]["process"]
            ret = proc.poll()
            status = "Работает" if ret is None else f"Остановлен (код {ret})"
            return {"output": f"Сервис {payload.service_id}:\nКоманда: {_bg_services[payload.service_id]['command']}\nСтатус: {status}\nPID: {proc.pid}"}
        return {"output": f"ОШИБКА: Сервис {payload.service_id} не найден."}
    else:
        lines = ["Активные фоновые процессы:"]
        for sid, info in list(_bg_services.items()):
            if sid.startswith(f"{payload.user_id}_"):
                ret = info["process"].poll()
                st = "Running" if ret is None else f"Exited({ret})"
                lines.append(f" - [{sid}] {info['command']} | Статус: {st}")
        return {"output": "\n".join(lines) if len(lines) > 1 else "Нет запущенных фоновых процессов."}

@router.post("/logs")
async def logs_service(payload: ServiceLogsPayload):
    if not payload.service_id.startswith(f"{payload.user_id}_"):
        raise HTTPException(status_code=403, detail="Доступ запрещен.")
    if payload.service_id in _bg_services:
        log_path = _bg_services[payload.service_id]["log_file"]
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    tail = lines[-payload.lines:] if payload.lines else lines
                    result_str = f"Логи сервиса {payload.service_id}:\n" + "".join(tail)
                    if not tail:
                        result_str += "[Лог пуст]"
                    return {"output": result_str}
            except Exception as e:
                return {"output": f"ОШИБКА чтения лога: {e}"}
        return {"output": "ОШИБКА: Файл лога не найден."}
    return {"output": f"ОШИБКА: Сервис {payload.service_id} не найден."}
