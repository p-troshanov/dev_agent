# backend/core/routers/tasks.py
import json
import os
import zipfile
import io
import re
import shutil
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, Depends
from backend.core.database import get_db
from backend.core.schemas import TaskCreate, TaskToolConfirm, TaskToolResponse, TaskPhaseUpdate, ManualActionRequest
from backend.core.tasks.runner import run_task
from backend.core.state import state
from backend.core.auth import get_current_user
from backend.core.llm import extract_json
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

BASE_WORKSPACE = os.getenv("WORKSPACE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../workspace")))

class TaskContinue(BaseModel):
    prompt: str

@router.get("")
def get_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''
                SELECT t.id, t.title, p.name as project_name, t.status, t.created_at,
                        t.agent_id, a.name, t.work_dir, t.auto_approve_tools,
                        COALESCE(SUM(ls.cost), 0.0) as total_cost, t.type, t.current_phase, t.target_action
                FROM tasks t
                LEFT JOIN agents a ON t.agent_id = a.id
                LEFT JOIN projects p ON t.project_id = p.id
                LEFT JOIN llm_statistics ls ON t.id = ls.task_id
                WHERE t.user_id = %s
                GROUP BY t.id, p.id, a.id
                ORDER BY t.id DESC
            ''', (user_id,))
            
            return [
                {
                    "id": r[0], 
                    "title": r[1], 
                    "project_name": r[2] or "",
                    "status": r[3], 
                    "created_at": r[4],
                    "agent_id": r[5],
                    "agent_name": r[6] or "",
                    "work_dir": r[7] or "",
                    "auto_approve_tools": bool(r[8]),
                    "total_cost": float(r[9]),
                    "type": r[10] or "standard",
                    "current_phase": r[11] or "discovery",
                    "target_action": r[12] or "full_execution"
                } for r in c.fetchall()
            ]

@router.post("")
async def create_task(data: TaskCreate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    target_work_dir = data.work_dir
    with get_db() as conn:
        with conn.cursor() as c:
            if data.project_id:
                c.execute("SELECT folder_name FROM projects WHERE id = %s AND user_id = %s", (data.project_id, user_id))
                p_row = c.fetchone()
                if p_row and p_row[0]:
                    target_work_dir = p_row[0].replace('\\', '/')

            auto_approve_val = 1 if data.auto_approve_tools else 0
            
            c.execute('INSERT INTO tasks (user_id, title, project_id, status, agent_id, work_dir, is_cancelled, auto_approve_tools, type, current_phase, target_action) VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s) RETURNING id',
                       (user_id, data.title, data.project_id, 'pending', data.agent_id, target_work_dir, auto_approve_val, data.type, 'discovery', data.target_action))
            task_id = c.fetchone()[0]
            
            c.execute('''INSERT INTO task_logs (task_id, role, content, agent_name)
                          VALUES (%s, %s, %s, %s)''',
                      (task_id, 'user', data.initial_prompt, ''))
        conn.commit()
        
    background_tasks.add_task(run_task, task_id, data.initial_prompt, False, user_id)
    return {"status": "ok", "id": task_id}

@router.post("/{task_id}/continue")
async def continue_task(task_id: int, data: TaskContinue, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('UPDATE tasks SET status = %s, is_cancelled = 0 WHERE id = %s AND user_id = %s', ('pending', task_id, user_id))
            c.execute('''INSERT INTO task_logs (task_id, role, content, agent_name)
                          VALUES (%s, %s, %s, %s)''',
                      (task_id, 'user', data.prompt, ''))
        conn.commit()
        
    background_tasks.add_task(run_task, task_id, data.prompt, True, user_id)
    return {"status": "ok"}

@router.post("/{task_id}/next_phase")
def next_task_phase(task_id: int, data: TaskPhaseUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE tasks SET current_phase = %s WHERE id = %s AND user_id = %s", (data.phase, task_id, user_id))
        conn.commit()
    return {"status": "ok"}

@router.post("/{task_id}/rollback")
def rollback_task(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT work_dir FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
            row = c.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Задача не найдена")
            work_dir = row[0]
            
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}"))
    target_dir = work_dir if work_dir else base_user_dir
    backup_dir = os.path.join(target_dir, ".backups", f"task_{task_id}")
    
    if not os.path.exists(backup_dir):
        raise HTTPException(status_code=400, detail="Бекапы для этой задачи не найдены")
        
    try:
        restored_count = 0
        for root, _, files in os.walk(backup_dir):
            for file in files:
                bak_path = os.path.join(root, file)
                rel_path = os.path.relpath(bak_path, backup_dir)
                orig_path = os.path.join(target_dir, rel_path)
                
                os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                shutil.copy2(bak_path, orig_path)
                restored_count += 1
                
        # Пишем в лог
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('''INSERT INTO task_logs (task_id, role, content, agent_name)
                              VALUES (%s, %s, %s, %s)''',
                          (task_id, 'system', f"Выполнен откат изменений. Восстановлено файлов: {restored_count}", 'Система'))
            conn.commit()
            
        return {"status": "ok", "message": f"Восстановлено файлов: {restored_count}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка восстановления: {str(e)}")

@router.get("/{task_id}/logs")
def get_task_logs(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id FROM tasks WHERE id = %s AND user_id = %s', (task_id, user_id))
            if not c.fetchone():
                raise HTTPException(status_code=404, detail="Task not found")
                
            c.execute('''SELECT id, role, content, agent_name, tool_call_id, created_at, pending_approval
                          FROM task_logs WHERE task_id = %s ORDER BY id ASC''', (task_id,))
            logs = c.fetchall()
            
            return [
                {
                    "id": r[0], 
                    "role": r[1], 
                    "content": r[2], 
                    "agent_name": r[3], 
                    "tool_call_id": r[4], 
                    "created_at": r[5],
                    "pending_approval": bool(r[6])
                } for r in logs
            ]

@router.get("/{task_id}/context_export")
def export_task_context(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''
                SELECT t.title, t.status, t.created_at, t.work_dir, a.name, a.system_prompt
                FROM tasks t
                LEFT JOIN agents a ON t.agent_id = a.id
                WHERE t.id = %s AND t.user_id = %s
            ''', (task_id, user_id))
            task_row = c.fetchone()
            
            if not task_row:
                return Response(content='{"error": "Task not found"}', status_code=404)
                
            t_title, t_status, t_created, t_work_dir, agent_name, agent_system_prompt = task_row
            
            c.execute('SELECT name, description, category, schema_json FROM user_tools WHERE is_active = 1 AND user_id = %s', (user_id,))
            all_tools = c.fetchall()

            c.execute('''
                SELECT role, content, agent_name, tool_call_id, created_at 
                FROM task_logs 
                WHERE task_id = %s 
                ORDER BY id ASC
            ''', (task_id,))
            logs = c.fetchall()

    tools_by_category = {}
    tools_map = {}
    for t_name, t_desc, t_cat, t_schema in all_tools:
        cat = t_cat or "Остальное"
        if cat not in tools_by_category:
            tools_by_category[cat] = []
        tools_by_category[cat].append(f"{t_name} - {t_desc}")
        try:
            tools_map[t_name] = json.loads(t_schema) if isinstance(t_schema, str) else t_schema
        except:
            pass

    tools_catalog_parts = []
    for cat, items in tools_by_category.items():
        tools_catalog_parts.append(f"{cat} ({', '.join(items)})")
    tools_catalog_text = ";\n".join(tools_catalog_parts) + "."

    real_base = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    fake_base = f"/workspace/user_{user_id}"
    fake_work = fake_base
    if t_work_dir:
        real_work = t_work_dir.replace('\\', '/')
        if real_work.startswith(real_base):
            rel = os.path.relpath(real_work, real_base).replace('\\', '/')
            if rel != '.':
                fake_work = f"{fake_base}/{rel}"

    dir_info = f"\n\nТекущая директория: {fake_work}\nКорень доступной файловой системы (sandbox) пользователя: {fake_base}." if fake_work else ""
    
    sys_prompt = (
        f"Ты системный агент '{agent_name or 'Агент'}'. "
        "Тебе передана вся история логов и список доступных инструментов.\n"
        "Твоя задача — проанализировать лог и выдать ответ в формате JSON, в котором ты должен выбрать какие инструменты использовать дальше.\n"
        "Обязательно включи инструмент 'finish_task', если считаешь что задача уже выполнена."
        f"{dir_info}"
    )

    messages = [{"role": "system", "content": sys_prompt}]
    messages.append({
        "role": "system",
        "content": f"Каталог инструментов:\n{tools_catalog_text}"
    })
    
    requested_tool_names = set()
    has_tool_request = False
    
    if logs:
        for r_role, r_content, r_agent, t_call_id, _ in logs:
            if r_role == 'system':
                continue
            if r_role == 'user':
                messages.append({"role": "user", "content": r_content})
                has_tool_request = False
                requested_tool_names.clear()
            elif r_role == 'assistant':
                messages.append({"role": "assistant", "content": r_content or "(Пустой ответ агента)"})
                if r_content and not t_call_id:
                    parsed = extract_json(r_content)
                    if isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, str):
                                requested_tool_names.add(item)
                        has_tool_request = True
            elif r_role == 'tool':
                messages.append({"role": "user", "content": f"Результат вызова инструмента ({r_agent}): {r_content}"})
                if r_agent:
                    m = re.search(r'\((.*?)\)', r_agent)
                    if m:
                        requested_tool_names.add(m.group(1))
                        has_tool_request = True
    else:
        messages.append({"role": "user", "content": "Лог пуст."})
        
    export_data = {
        "model": "gpt-4o",
        "messages": messages
    }
    
    if has_tool_request:
        if "finish_task" not in requested_tool_names:
            requested_tool_names.add("finish_task")
        active_schemas = []
        for name in requested_tool_names:
            if name in tools_map:
                active_schemas.append(tools_map[name])
        formatted_tools = [s if "type" in s else {"type": "function", "function": s} for s in active_schemas]
        if formatted_tools:
            export_data["tools"] = formatted_tools
            
    output = json.dumps(export_data, ensure_ascii=False, indent=2)
    headers = {"Content-Disposition": f"attachment; filename=task_payload_{task_id}.json"}
    return Response(content=output, media_type="application/json; charset=utf-8", headers=headers)

@router.get("/{task_id}/debug_export")
def export_task_debug(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
    debug_dir = os.path.join(base_user_dir, ".debug", f"task_{task_id}").replace('\\', '/')
    
    if not os.path.exists(debug_dir) or not os.listdir(debug_dir):
        raise HTTPException(status_code=404, detail="Отладочные логи для этой задачи не найдены")
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(debug_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file).replace('\\', '/')
                    arcname = file
                    zip_file.write(file_path, arcname)
                    
    zip_buffer.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=task_debug_{task_id}.zip"}
    return Response(content=zip_buffer.getvalue(), media_type="application/zip", headers=headers)

@router.post("/{task_id}/cancel")
def cancel_task(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE tasks SET is_cancelled = 1, status = 'failed' WHERE id = %s AND user_id = %s", (task_id, user_id))
        conn.commit()
        
    if task_id in state.pending_task_tools:
        future = state.pending_task_tools[task_id]
        if not future.done():
            future.set_result(False)
            
    return {"status": "ok"}

@router.post("/{task_id}/approve_tool")
def approve_task_tool(task_id: int, data: TaskToolConfirm, current_user: dict = Depends(get_current_user)):
    future = state.pending_task_tools.get(data.tool_call_id)
    if future and not future.done():
        future.set_result(data.approved)
        
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE task_logs SET pending_approval = 0 WHERE task_id = %s AND tool_call_id = %s", (task_id, data.tool_call_id))
        conn.commit()
        
    return {"status": "ok"}

@router.post("/{task_id}/submit_tool_response")
def submit_task_tool_response(task_id: int, data: TaskToolResponse, current_user: dict = Depends(get_current_user)):
    future = state.pending_task_tools.get(data.tool_call_id)
    if future and not future.done():
        future.set_result(data.response_text)
        
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE task_logs SET pending_approval = 0 WHERE task_id = %s AND tool_call_id = %s", (task_id, data.tool_call_id))
        conn.commit()
        
    return {"status": "ok"}

@router.post("/{task_id}/manual_action")
async def manual_task_action(task_id: int, data: ManualActionRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT work_dir, project_id FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
            row = c.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Task not found")
            work_dir = row[0]
            project_id = row[1]

    from backend.core.tasks.tools_impl.system import execute_system_tool
    from backend.core.tasks.tools_impl.utils import _call_tool_node

    result_str = ""

    if data.action == "clear_folder":
        target_dir = work_dir
        if not target_dir or target_dir == "/":
             return {"status": "error", "result": "Invalid work_dir"}
        
        # Безопасно очищаем содержимое, не трогая .git и .backups
        cmd = "find . -mindepth 1 -not -path './.git*' -not -path './.backups*' -delete"
        res = await _call_tool_node("/api/terminal/run", {"command": cmd, "work_dir": target_dir, "user_id": user_id})
        try:
            res_data = json.loads(res)
            result_str = res_data.get("output", res)
        except:
            result_str = res
        result_str = f"Папка очищена.\n{result_str}"

    elif data.action == "github_pull":
        res = await execute_system_tool("github_sync", {"action": "clone_or_pull", "project_id": project_id}, work_dir, "", "", None, user_id, task_id, "manual", {})
        result_str = res.get("result_str", "Ошибка выполнения")

    elif data.action == "github_push":
        res = await execute_system_tool("github_sync", {"action": "push", "project_id": project_id, "commit_message": "Manual push from UI"}, work_dir, "", "", None, user_id, task_id, "manual", {})
        result_str = res.get("result_str", "Ошибка выполнения")

    elif data.action == "check_syntax":
        cmd = 'echo "=== Python ==="; find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/venv/*" -exec python3 -m py_compile {} + 2>&1; echo "=== JS/TS ==="; find . -name "*.js" -o -name "*.ts" -not -path "*/node_modules/*" -exec node --check {} + 2>&1 || true'
        res = await _call_tool_node("/api/terminal/run", {"command": cmd, "work_dir": work_dir, "user_id": user_id})
        try:
            res_data = json.loads(res)
            result_str = res_data.get("output", res)
        except:
            result_str = res

    else:
        result_str = "Неизвестное действие"

    return {"status": "ok", "result": result_str}
