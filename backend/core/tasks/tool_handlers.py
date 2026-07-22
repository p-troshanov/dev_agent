# backend/core/tasks/tool_handlers.py
import json
import asyncio
import os
import shutil

from backend.core.database import get_db
from backend.core.state import state
from backend.core.tasks.tools_impl.utils import _call_tool_node, _hide_host_path
from backend.core.tasks.tools_impl.fs_code import execute_fs_code_tool
from backend.core.tasks.tools_impl.system import execute_system_tool

async def handle_tool_call(f_name: str, args: dict, work_dir: str, last_modified_file: str, last_backup_file: str, agent_id: int = None, user_id: int = None, task_id: int = None, tool_call_id: str = None) -> dict:
    needs_approval = False
    auto_approve_flag = False
    
    if task_id:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT auto_approve_tools FROM tasks WHERE id = %s", (task_id,))
                row = c.fetchone()
                if row: auto_approve_flag = bool(row[0])
                
    if user_id:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT requires_approval FROM user_tools WHERE name = %s AND user_id = %s", (f_name, user_id))
                row = c.fetchone()
                if row and row[0] == 1: needs_approval = True
                
    if f_name in ["ask_user", "message_user", "github_sync"]: 
        needs_approval = True
        
    if f_name in ["run_terminal", "manage_background_service"]:
        cmd = args.get("command", "").lower()
        dangerous_patterns = ["rm ", "rmdir ", "del ", "rd ", "format ", "diskpart", "mkfs", "drop ", "truncate "]
        if any(cmd.startswith(p.strip()) or f" {p}" in cmd or f"& {p}" in cmd or f"| {p}" in cmd for p in dangerous_patterns):
            needs_approval = True
            
    if auto_approve_flag and f_name not in ["ask_user", "message_user"]:
        needs_approval = False
        
    if needs_approval and task_id and tool_call_id:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('UPDATE tasks SET status = %s WHERE id = %s', ('waiting_user', task_id))
            conn.commit()
            
        await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
        
        warning_msg = f"Ожидается подтверждение для: {f_name}"
        if f_name in ["run_terminal", "manage_background_service"]:
            warning_msg = f"Команда:\n`{args.get('command', '')}`\n\nРазрешить выполнение?"
        elif f_name in ["ask_user", "message_user"]:
            warning_msg = f"Сообщение от агента:\n**{args.get('question', args.get('message', 'Нет сообщения.'))}**"
            
        approval_payload = {
            "is_plugin_request": True,
            "tool_name": f_name,
            "args": args,
            "message": warning_msg
        }
        
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('''INSERT INTO task_logs (task_id, role, content, agent_name, tool_call_id, pending_approval)
                              VALUES (%s, %s, %s, %s, %s, %s)''', (task_id, "tool", json.dumps(approval_payload, ensure_ascii=False), f"Плагин ({f_name})", tool_call_id, 1))
            conn.commit()
            
        future = asyncio.Future()
        state.pending_task_tools[tool_call_id] = future
        
        try:
            approved = await future
        finally:
            if tool_call_id in state.pending_task_tools:
                del state.pending_task_tools[tool_call_id]
                
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute('UPDATE tasks SET status = %s WHERE id = %s', ('running', task_id))
            conn.commit()
            
        await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
        
        if f_name in ["ask_user", "message_user"]:
            if isinstance(approved, str):
                return {"result_str": f"Ответ пользователя: {approved}", "abort_subsequent_tools": False}
            else:
                return {"result_str": "[Пользователь отменил действие].", "abort_subsequent_tools": False}
                
        if isinstance(approved, str):
            try:
                plugin_data = json.loads(approved)
                if plugin_data.get("action") == "modify_args":
                    args.update(plugin_data.get("new_args", {}))
                    approved = True
                elif plugin_data.get("action") == "resolve_tool":
                    return {"result_str": plugin_data.get("result_str", "Выполнено."), "abort_subsequent_tools": False}
                else:
                    approved = True
            except:
                approved = True
                
        if not approved:
            return {"result_str": "[Действие отклонено пользователем].", "abort_subsequent_tools": False}

    tool_settings = {}
    if user_id:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT settings FROM user_tools WHERE name = %s AND user_id = %s", (f_name, user_id))
                row = c.fetchone()
                if row and row[0]:
                    tool_settings = row[0] if isinstance(row[0], dict) else json.loads(row[0])

    FS_CODE_TOOLS = {"read_file", "check_file_exists", "write_file", "edit_file", "create_directory", "attach_file", "scan_project", "restore_backup", "check_syntax", "install_dependencies", "view_file_diff"}
    SYSTEM_TOOLS = {"run_terminal", "manage_background_service", "get_service_logs", "manage_agent", "delegate_task", "github_sync", "summarize_text", "finish_task"}

    if f_name in FS_CODE_TOOLS:
        res_dict = await execute_fs_code_tool(f_name, args, work_dir, last_modified_file, last_backup_file, agent_id, user_id, task_id, tool_call_id, tool_settings)
    elif f_name in SYSTEM_TOOLS:
        res_dict = await execute_system_tool(f_name, args, work_dir, last_modified_file, last_backup_file, agent_id, user_id, task_id, tool_call_id, tool_settings)
    else:
        res_dict = {
            "endpoint": None, "payload": {}, "file_path": None, "abort_subsequent_tools": False,
            "result_str": f"Неизвестный инструмент {f_name} (не зарегистрирован).",
            "last_modified_file": last_modified_file, "last_backup_file": last_backup_file
        }

    endpoint = res_dict.get("endpoint")
    payload = res_dict.get("payload", {})
    result_str = res_dict.get("result_str", "")
    file_path = res_dict.get("file_path")
    abort_subsequent_tools = res_dict.get("abort_subsequent_tools", False)
    last_modified_file = res_dict.get("last_modified_file")
    last_backup_file = res_dict.get("last_backup_file")

    if endpoint:
        raw_result = await _call_tool_node(endpoint, payload)
        
        try:
            res_data = json.loads(raw_result)
            if isinstance(res_data, dict):
                if "output" in res_data:
                    result_str = res_data["output"]
                elif "message" in res_data:
                    result_str = res_data["message"]
                elif "content" in res_data:
                    result_str = res_data["content"]
                else:
                    result_str = raw_result
            else:
                result_str = raw_result
        except:
            result_str = raw_result
            
        if f_name in ["write_file", "edit_file"] and "Ошибка" not in result_str and "ok" not in result_str and "error" not in result_str.lower():
            result_str += f"\n\n[Действие выполнено для: {file_path}]"
            
        if f_name in ["run_terminal", "install_dependencies", "check_syntax"]:
            lower_res = result_str.lower()
            has_error = False
            
            try:
                res_data = json.loads(raw_result)
                if isinstance(res_data, dict) and res_data.get("return_code", 0) != 0:
                    has_error = True
            except:
                pass
                
            if not has_error:
                has_error = any(err in lower_res for err in [
                    "traceback (most recent call last):",
                    "modulenotfounderror:",
                    "syntaxerror:",
                    "fatal error:",
                    "exception:"
                ])
                
            if has_error:
                if last_modified_file and last_backup_file and os.path.exists(last_backup_file):
                    try:
                        shutil.copy2(last_backup_file, last_modified_file)
                        result_str += f"\n\n[Замечена ошибка! Файл {last_modified_file} был автоматически восстановлен из бэкапа.]"
                    except Exception:
                        pass
                
                if f_name == "run_terminal":
                    result_str += "\n\n[Команда завершилась с ошибкой. Проанализируй логи и исправь ошибку.]"
                else:
                    result_str += "\n\n[Синтаксис кода содержит ошибку или не удалось установить зависимости. Изменения откачены. Попробуй исправить скрипт.]"
                abort_subsequent_tools = True

    if f_name not in ["run_terminal", "install_dependencies", "check_syntax"] and (result_str.startswith("Ошибка:") or result_str.startswith("Error:") or result_str.startswith("Exception:")):
        abort_subsequent_tools = True
        
    result_str = _hide_host_path(result_str, user_id)
    
    if last_modified_file: last_modified_file = last_modified_file.replace('\\', '/')
    if last_backup_file: last_backup_file = last_backup_file.replace('\\', '/')

    return {
        "result_str": result_str,
        "abort_subsequent_tools": abort_subsequent_tools,
        "last_modified_file": last_modified_file,
        "last_backup_file": last_backup_file
    }
