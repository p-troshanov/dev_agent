# backend/core/tasks/runner.py
import json
import os
import traceback
from backend.core.database import get_db
from backend.core.state import state
from backend.core.tasks.runner_db import log_task_action, update_task_status
from backend.core.tasks.runner_context import setup_task_workspace, build_system_prompt, build_initial_messages, get_active_manager_tools
from backend.core.tasks.runner_loop import run_task_loop

async def run_task(task_id: int, initial_prompt: str, is_continue: bool = False, user_id: int = None):
    update_task_status(task_id, 'running')
    await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
    log_task_action(task_id, "system", "Продолжение задачи..." if is_continue else "Старт задачи...", "")
    
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('''
                    SELECT t.agent_id, a.name, a.system_prompt, a.model, t.work_dir, t.auto_approve_tools, a.settings, t.project_id, t.type, t.current_phase, t.target_action
                    FROM tasks t LEFT JOIN agents a ON t.agent_id = a.id WHERE t.id = %s
                ''', (task_id,))
                row = c.fetchone()
                
                c.execute("SELECT user_name FROM user_settings WHERE user_id = %s", (user_id,))
                settings_row = c.fetchone()
                user_name = settings_row[0] if settings_row else "Пользователь"
                
        if not row:
            log_task_action(task_id, "system", "Ошибка: Задача не найдена.", "")
            update_task_status(task_id, 'failed')
            await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
            return
            
        agent_id, agent_name, agent_system_prompt, agent_model, work_dir, auto_approve_tools, agent_settings_raw, project_id, task_type, current_phase, target_action = row
        if not agent_name: agent_name = "Ассистент"
        auto_approve_flag = bool(auto_approve_tools)
        
        agent_settings = {}
        if agent_settings_raw:
            try: agent_settings = json.loads(agent_settings_raw) if isinstance(agent_settings_raw, str) else agent_settings_raw
            except: pass
            
        work_dir = setup_task_workspace(user_id, task_id, work_dir)

        # Контекст проекта
        project_context = ""
        if project_id:
            with get_db() as conn:
                with conn.cursor() as c:
                    c.execute("SELECT name, description, settings FROM projects WHERE id = %s", (project_id,))
                    p_row = c.fetchone()
                    if p_row:
                        p_name, p_desc, p_settings_raw = p_row
                        p_settings = {}
                        try: 
                            p_settings = json.loads(p_settings_raw) if isinstance(p_settings_raw, str) else (p_settings_raw or {})
                        except: 
                            pass
                        
                        project_context += f"--- Контекст проекта ---\n"
                        project_context += f"Название: {p_name}\n"
                        if p_desc and p_desc.strip():
                            project_context += f"Описание: {p_desc.strip()}\n"
                        
                        for k, v in p_settings.items():
                            if v and str(v).strip():
                                project_context += f"{k}: {v}\n"

        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('SELECT name, description, schema_json FROM user_tools WHERE is_active = 1 AND user_id = %s', (user_id,))
                all_tools = c.fetchall()
        
        tools_map = {}
        tools_desc_map = {}
        for t_name, t_desc, t_schema in all_tools:
            tools_desc_map[t_name] = t_desc or ""
            try:
                tools_map[t_name] = json.loads(t_schema) if isinstance(t_schema, str) else t_schema
            except:
                pass
        
        sys_prompt = build_system_prompt(agent_name, user_id, work_dir, tools_desc_map, task_type, current_phase)
        
        # Сборка финального промпта (sys_prompt идет последним для жесткости)
        full_prompt_parts = []
        if agent_system_prompt and agent_system_prompt.strip():
            full_prompt_parts.append(agent_system_prompt.strip())
        if project_context:
            full_prompt_parts.append(project_context.strip())
        full_prompt_parts.append(sys_prompt)
        
        sys_prompt = "\n\n---\n\n".join(full_prompt_parts)
        
        messages = build_initial_messages(task_id, initial_prompt, is_continue)
        active_tools_schemas = get_active_manager_tools(tools_map, task_type, current_phase)
        
        await run_task_loop(
            task_id=task_id,
            user_id=user_id,
            messages=messages,
            sys_prompt=sys_prompt,
            agent_name=agent_name,
            agent_model=agent_model,
            agent_settings=agent_settings,
            work_dir=work_dir,
            active_tools_schemas=active_tools_schemas,
            agent_id=agent_id
        )

    except Exception as e:
        print(f"[RUNNER] Fatal error in task {task_id}: {e}\n{traceback.format_exc()}", flush=True)
        log_task_action(task_id, "system", f"Фатальная ошибка: {str(e)}", "")
        update_task_status(task_id, 'failed')
        await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
