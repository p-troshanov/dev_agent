# backend/core/tasks/runner_context.py
import os
import json
import re
from datetime import datetime
from backend.core.database import get_db

_default_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../workspace"))
_env_workspace = os.getenv("WORKSPACE_DIR")

if _env_workspace and os.name == 'nt' and _env_workspace.startswith('/'):
    BASE_WORKSPACE = _default_workspace
else:
    BASE_WORKSPACE = _env_workspace or _default_workspace

def setup_task_workspace(user_id: int, task_id: int, work_dir: str) -> str:
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    os.makedirs(base_user_dir, exist_ok=True)
    
    fake_base = f"/workspace/user_{user_id}"
    
    if work_dir:
        work_dir = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff]', '', str(work_dir)).strip()
        work_dir = work_dir.replace('\\', '/')
        if work_dir.startswith(fake_base):
            rel = work_dir[len(fake_base):].lstrip('/')
            work_dir = os.path.normpath(os.path.join(base_user_dir, rel)).replace('\\', '/')
        elif not os.path.isabs(work_dir):
            work_dir = os.path.normpath(os.path.join(base_user_dir, work_dir)).replace('\\', '/')
            
    if not work_dir or not work_dir.startswith(base_user_dir):
        work_dir = base_user_dir
        
    os.makedirs(work_dir, exist_ok=True)
    
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('UPDATE tasks SET work_dir = %s WHERE id = %s', (work_dir, task_id))
        conn.commit()
        
    return work_dir


def build_system_prompt(agent_name: str, user_id: int, work_dir: str, tools_desc_map: dict) -> str:
    real_base = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    fake_base = f"/workspace/user_{user_id}"
    
    fake_work = fake_base
    if work_dir:
        real_work = work_dir.replace('\\', '/')
        if real_work.startswith(real_base):
            rel = os.path.relpath(real_work, real_base).replace('\\', '/')
            if rel != '.':
                fake_work = f"{fake_base}/{rel}"
                
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # --- ДИНАМИЧЕСКИЙ КОНТЕКСТ ОС ДЛЯ АГЕНТА ---
    os_hint = ""
    if os.name == 'nt':
        os_hint = "5. ВАЖНО: Терминал работает в среде Windows (cmd.exe). Команды Linux (ls, rm, pwd) НЕ РАБОТАЮТ! Используйте аналоги Windows (dir, del, cd) или кроссплатформенные утилиты (git, python). Пути пишите в формате Linux (/workspace/...), система сама их переведет.\n"
    else:
        os_hint = "5. ВАЖНО: Терминал работает в среде Linux (bash).\n"
        
    sys_prompt = (
        f"Вы автономный агент '{agent_name}'.\n"
        f"Текущее системное время: {current_time}\n"
        "Ваша задача — выполнить порученную пользователем задачу (instruction) от начала и до конца.\n"
        f"Текущая рабочая директория: {fake_work}.\n"
        "Правила выполнения:\n"
        "1. Выполняйте всю работу в текущей рабочей директории, если не сказано иное.\n"
        f"2. Вы не можете выходить за пределы корневой папки {fake_base}.\n"
        "3. Внимательно читайте результаты выполнения команд и ошибки, исправляйте их.\n"
        "4. Вы ОБЯЗАНЫ в любом случае ответить пользователю, используя хотя бы один инструмент. Используйте 'message_user', чтобы задать вопрос (is_final=false) или завершить задачу (is_final=true).\n"
        f"{os_hint}"
    )
    return sys_prompt


def build_initial_messages(task_id: int, initial_prompt: str, is_continue: bool) -> list:
    messages = []
    if is_continue:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT role, content, agent_name, tool_call_id, created_at FROM task_logs WHERE task_id = %s ORDER BY id ASC", (task_id,))
                logs = c.fetchall()
                
        for r_role, r_content, r_agent, t_call_id, created_at in logs:
            if r_role == 'system': 
                continue
                
            time_str = created_at.strftime("%H:%M:%S") if hasattr(created_at, 'strftime') else ""
            ts_prefix = f"[{time_str}] " if time_str else ""
            
            if r_role == 'user':
                messages.append({"role": "user", "content": f"{ts_prefix}{r_content}"})
            elif r_role == 'assistant':
                messages.append({"role": "assistant", "content": f"{ts_prefix}{r_content or '(пустой ответ)'}"})
            elif r_role == 'tool':
                messages.append({"role": "user", "content": f"{ts_prefix}Ответ ({r_agent}): {r_content}"})
                
        current_time = datetime.now().strftime("%H:%M:%S")
        messages.append({"role": "user", "content": f"[{current_time}] Продолжение: {initial_prompt}"})
    else:
        current_time = datetime.now().strftime("%H:%M:%S")
        messages.append({"role": "user", "content": f"[{current_time}] {initial_prompt}"})
    return messages


def get_active_manager_tools(tools_map: dict) -> list:
    active_tools_schemas = []
    exclude_tools = {"manage_agent", "delegate_task", "ask_user", "finish_task"}
    for name, schema in tools_map.items():
        if name not in exclude_tools:
            active_tools_schemas.append(schema)
    return active_tools_schemas
