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

def build_system_prompt(agent_name: str, user_id: int, work_dir: str, tools_desc_map: dict, task_type: str = "standard", current_phase: str = "discovery") -> str:
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
    
    # --- Выявление ОС для корректных команд ---
    os_hint = ""
    if os.name == 'nt':
        os_hint = "5. Система работает на Windows (cmd.exe). Использовать Linux утилиты (ls, rm, pwd) нельзя, используй аналоги Windows (dir, del, cd) или скрипты (git, python). Корневой путь Linux (/workspace/...), маппится автоматически, его можно использовать.\n"
    else:
        os_hint = "5. Система работает на Linux (bash).\n"
        
    base_sys_prompt = (
        f"Тебя зовут '{agent_name}'.\n"
        f"Текущее время: {current_time}\n"
        "Выполняй запросы пользователя (instruction) точно и по делу.\n"
        f"Директория проекта: {fake_work}.\n"
        "Правила использования инструментов:\n"
        "1. Инструменты возвращают сырой текст.\n"
        f"2. Твоя корневая папка ограничена {fake_base}.\n"
        "3. Вызывай функции строго по JSON-схеме.\n"
        "4. Для общения с пользователем вызывай 'message_user', если ждешь ответа (is_final=false) или хочешь завершить задачу (is_final=true).\n"
        f"{os_hint}"
    )

    if task_type == "step_by_step":
        phase_instruction = ""
        if current_phase == "discovery":
            phase_instruction = "Твоя цель сейчас: изучить структуру проекта и запросить содержимое файлов, которые нужны для решения задачи. Не пытайся писать код или предлагать решения на этом этапе. Узнай всё, что нужно для составления плана, и сообщи пользователю, что ты готов к следующему шагу."
        elif current_phase == "planning":
            phase_instruction = "Твоя цель сейчас: составить пошаговый план решения или задать уточняющие вопросы пользователю. Никаких изменений файлов не делай (инструменты изменения отключены). Пользователь должен утвердить план."
        elif current_phase == "execution":
            phase_instruction = "Твоя цель сейчас: применить утвержденный план и внести изменения в код с помощью инструментов. Будь осторожен и вноси изменения аккуратно."
            
        sys_prompt = f"{base_sys_prompt}\n\n--- ВАЖНО: ТЕКУЩАЯ ФАЗА ЗАДАЧИ: {current_phase.upper()} ---\n{phase_instruction}"
    else:
        sys_prompt = base_sys_prompt
        
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
                messages.append({"role": "assistant", "content": f"{ts_prefix}{r_content or '(Вызван инструмент)'}"})
            elif r_role == 'tool':
                messages.append({"role": "user", "content": f"{ts_prefix}Результат инструмента ({r_agent}): {r_content}"})
                
        current_time = datetime.now().strftime("%H:%M:%S")
        messages.append({"role": "user", "content": f"[{current_time}] Пользователь: {initial_prompt}"})
    else:
        current_time = datetime.now().strftime("%H:%M:%S")
        messages.append({"role": "user", "content": f"[{current_time}] {initial_prompt}"})
    return messages

def get_active_manager_tools(tools_map: dict, task_type: str = "standard", current_phase: str = "discovery") -> list:
    active_tools_schemas = []
    exclude_tools = {"manage_agent", "delegate_task", "ask_user", "finish_task"}
    
    if task_type == "step_by_step":
        if current_phase == "discovery":
            # На этапе сбора контекста запрещаем модификацию файлов
            exclude_tools.update({"write_file", "edit_file", "create_directory", "run_terminal", "install_dependencies", "github_sync", "manage_background_service"})
        elif current_phase == "planning":
            # На этапе планирования отключаем ВООБЩЕ все файловые инструменты, оставляем только message_user
            exclude_tools.update({"write_file", "edit_file", "create_directory", "run_terminal", "install_dependencies", "github_sync", "manage_background_service", "read_file", "check_file_exists", "scan_project", "restore_backup", "view_file_diff"})
        # На execution доступны все (или те, которые оставим)

    for name, schema in tools_map.items():
        if name not in exclude_tools:
            active_tools_schemas.append(schema)
    return active_tools_schemas
