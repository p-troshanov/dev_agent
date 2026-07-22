# backend/core/tasks/tools_impl/system.py
import os
import json
import time
import re
import urllib.parse
import urllib.request
import subprocess
import requests
import asyncio
from backend.core.database import get_db
from backend.core.state import state
from backend.core.tasks.tools_impl.utils import _resolve_path, _call_tool_node, _hide_host_path
from backend.core.llm import generate_response

BASE_WORKSPACE = os.getenv("WORKSPACE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../workspace")))

def _strip_zwsp(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)

async def execute_system_tool(f_name: str, args: dict, work_dir: str, last_modified_file: str, last_backup_file: str, agent_id: int, user_id: int, task_id: int, tool_call_id: str, tool_settings: dict) -> dict:
    res = {
        "endpoint": None, "payload": {}, "result_str": "",
        "file_path": None, "abort_subsequent_tools": False,
        "last_modified_file": last_modified_file, "last_backup_file": last_backup_file
    }
    
    if f_name == "run_terminal":
        command = _strip_zwsp(args.get("command", ""))
        res["endpoint"], res["payload"] = "/api/terminal/run", {"command": command, "work_dir": args.get("work_dir", work_dir), "user_id": user_id}
        
    elif f_name == "manage_background_service":
        action = _strip_zwsp(args.get("action", "status"))
        t_work_dir = _resolve_path(args.get("work_dir", work_dir), work_dir, user_id)
        
        if action == "start":
            command = _strip_zwsp(args.get("command", ""))
            res["endpoint"], res["payload"] = "/api/service/start", {"command": command, "work_dir": t_work_dir, "user_id": user_id}
        elif action == "stop":
            service_id = _strip_zwsp(args.get("service_id", ""))
            res["endpoint"], res["payload"] = "/api/service/stop", {"service_id": service_id, "user_id": user_id}
        elif action == "status":
            service_id = _strip_zwsp(args.get("service_id", ""))
            res["endpoint"], res["payload"] = "/api/service/status", {"service_id": service_id, "user_id": user_id}

    elif f_name == "get_service_logs":
        service_id = _strip_zwsp(args.get("service_id", ""))
        res["endpoint"], res["payload"] = "/api/service/logs", {"service_id": service_id, "lines": args.get("lines", 50), "user_id": user_id}

    elif f_name == "manage_agent":
        action = args.get("action")
        if not user_id:
            res["result_str"] = "Ошибка: user_id обязателен."
        elif action == "create":
            agent_data = args.get("agent_data", {})
            name = agent_data.get("name", "Новый агент")
            description = agent_data.get("description", "")
            system_prompt = agent_data.get("system_prompt", "")
            model = agent_data.get("model", None)
            
            tools_list = agent_data.get("tools", [])
            settings_obj = agent_data.get("settings", {})
            
            try:
                with get_db() as conn:
                    with conn.cursor() as c:
                        c.execute('''INSERT INTO agents (user_id, name, description, model, system_prompt, skills, tools, settings, is_default, is_main)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                                  (user_id, name, description, model, system_prompt, "{}", json.dumps(tools_list), json.dumps(settings_obj), 0, 0))
                        new_id = c.fetchone()[0]
                    conn.commit()
                res["result_str"] = f"Агент '{name}' успешно создан с ID: {new_id}"
            except Exception as e:
                res["result_str"] = f"Ошибка: {e}"
                
        elif action == "update":
            upd_agent_id = args.get("agent_id")
            agent_data = args.get("agent_data", {})
            if not upd_agent_id:
                res["result_str"] = "Ошибка: agent_id обязателен для update"
            else:
                try:
                    updates = []
                    params = []
                    for k in ["name", "description", "system_prompt", "model"]:
                        if k in agent_data:
                            updates.append(f"{k} = %s")
                            params.append(agent_data[k])
                                            
                    if "tools" in agent_data:
                        updates.append("tools = %s")
                        params.append(json.dumps(agent_data["tools"]))
                    if "settings" in agent_data:
                        updates.append("settings = %s")
                        params.append(json.dumps(agent_data["settings"]))
                        
                    if not updates:
                        res["result_str"] = "Нет данных для обновления."
                    else:
                        params.extend([upd_agent_id, user_id])
                        query = f"UPDATE agents SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
                        with get_db() as conn:
                            with conn.cursor() as c:
                                c.execute(query, tuple(params))
                                if c.rowcount == 0:
                                    res["result_str"] = "Агент не найден или нет прав."
                                else:
                                    res["result_str"] = f"Агент ID {upd_agent_id} успешно обновлен."
                            conn.commit()
                except Exception as e:
                    res["result_str"] = f"Ошибка: {e}"
                    
        elif action == "delete":
            del_agent_id = args.get("agent_id")
            if not del_agent_id:
                res["result_str"] = "Ошибка: agent_id обязателен для delete"
            else:
                try:
                    with get_db() as conn:
                        with conn.cursor() as c:
                            c.execute("DELETE FROM agents WHERE id = %s AND user_id = %s", (del_agent_id, user_id))
                            if c.rowcount == 0:
                                res["result_str"] = "Агент не найден или нет прав."
                            else:
                                res["result_str"] = f"Агент ID {del_agent_id} удален."
                        conn.commit()
                except Exception as e:
                    res["result_str"] = f"Ошибка: {e}"
        else:
            res["result_str"] = f"Неизвестное действие '{action}'"

    elif f_name == "delegate_task":
        agent_target = args.get("agent_name", "")
        instruction = args.get("instruction", "")
        
        if not agent_target or not instruction:
            res["result_str"] = "Укажите agent_name и instruction."
        else:
            with get_db() as conn:
                with conn.cursor() as c:
                    c.execute("SELECT id, description, system_prompt, model, tools, settings, profession FROM agents WHERE name = %s AND (user_id = %s OR user_id IS NULL)", (agent_target, user_id))
                    row = c.fetchone()
            
            if not row:
                res["result_str"] = f"Агент '{agent_target}' не найден. Создайте его через manage_agent."
            else:
                sub_agent_id, sub_desc, sub_prompt, sub_model, sub_tools, sub_settings, sub_profession = row
                
                try: sub_tools_list = json.loads(sub_tools) if isinstance(sub_tools, str) else (sub_tools or [])
                except: sub_tools_list = []
                
                try: sub_settings_obj = json.loads(sub_settings) if isinstance(sub_settings, str) else (sub_settings or {})
                except: sub_settings_obj = {}
                
                active_schemas = []
                if sub_tools_list:
                    with get_db() as conn:
                        with conn.cursor() as c:
                            c.execute("SELECT name, schema_json FROM user_tools WHERE is_active = 1 AND user_id = %s", (user_id,))
                            for tn, tsch in c.fetchall():
                                if tn in sub_tools_list:
                                    try: active_schemas.append(json.loads(tsch) if isinstance(tsch, str) else tsch)
                                    except: pass
                                    
                formatted_tools = [s if "type" in s else {"type": "function", "function": s} for s in active_schemas]
                
                sub_messages = [{"role": "user", "content": instruction}]
                
                fake_base = f"/workspace/user_{user_id}"
                fake_work = fake_base
                real_base = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
                if work_dir:
                    real_work = work_dir.replace('\\', '/')
                    if real_work.startswith(real_base):
                        rel = os.path.relpath(real_work, real_base).replace('\\', '/')
                        if rel != '.': fake_work = f"{fake_base}/{rel}"
                
                sub_sys_prompt = f"Ваша роль: {sub_profession or 'Помощник'} ('{agent_target}').\n{sub_prompt or ''}\n\nРабочая директория (песочница): {fake_work}. Обязательно вызовите 'finish_task' с результатами работы, когда закончите."
                
                sub_result = ""
                sub_last_mod = last_modified_file
                sub_last_bak = last_backup_file
                execution_trace = []
                
                is_sub_finished = False
                llm_failed = False
                for step in range(20): 
                    kwargs = {"system_prompt": sub_sys_prompt, "agent_name": agent_target, "model_override": sub_model, "user_id": user_id, "task_id": task_id}
                    if formatted_tools:
                        kwargs["tools"] = formatted_tools
                        kwargs["tool_choice"] = "auto"
                        
                    if sub_settings_obj:
                        kwargs.update(sub_settings_obj)
                        
                    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}")).replace('\\', '/')
                    debug_dir = None
                    if task_id:
                        debug_dir = os.path.join(base_user_dir, ".debug", f"task_{task_id}")
                        
                    if debug_dir:
                        os.makedirs(debug_dir, exist_ok=True)
                        
                        payload_to_save = {
                            "system_prompt": sub_sys_prompt,
                            "messages": sub_messages,
                            "agent_name": agent_target,
                            "model_override": sub_model,
                        }
                        if formatted_tools:
                            payload_to_save["tools"] = kwargs.get("tools", [])
                        if sub_settings_obj:
                            payload_to_save.update(sub_settings_obj)
                            
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        debug_file_path = os.path.join(debug_dir, f"subagent_{agent_target}_step_{step}_{timestamp}.json")
                        try:
                            with open(debug_file_path, "w", encoding="utf-8") as f:
                                json.dump(payload_to_save, f, ensure_ascii=False, indent=2)
                        except Exception as e:
                            print(f"Ошибка сохранения debug-файла: {e}")

                    resp = await generate_response(sub_messages, **kwargs)
                    if not resp or not resp.choices:
                        sub_result = "Ошибка вызова LLM субагента (Rate limit или API недоступно)."
                        llm_failed = True
                        break
                        
                    sub_msg = resp.choices[0].message
                    
                    if hasattr(sub_msg, 'tool_calls') and sub_msg.tool_calls:
                        ast_msg = {"role": "assistant", "content": sub_msg.content or "", "tool_calls": []}
                        for tc in sub_msg.tool_calls:
                            ast_msg["tool_calls"].append({
                                "id": getattr(tc, "id", "unknown_id"), "type": "function",
                                "function": {"name": getattr(tc.function, "name", ""), "arguments": getattr(tc.function, "arguments", "")}
                            })
                        sub_messages.append(ast_msg)
                        
                        abort_chain = False
                        from backend.core.tasks.tool_handlers import handle_tool_call
                        for tc in sub_msg.tool_calls:
                            tc_name = getattr(tc.function, "name", "")
                            tc_id_val = getattr(tc, "id", f"sub_{time.time()}")
                            try: tc_args = json.loads(getattr(tc.function, "arguments", "{}"))
                            except: tc_args = {}
                            
                            tc_res = await handle_tool_call(
                                tc_name, tc_args, work_dir, sub_last_mod, sub_last_bak, 
                                sub_agent_id, user_id, task_id=task_id, tool_call_id=tc_id_val
                            )
                            tc_result_str = tc_res.get("result_str", "")
                            sub_last_mod = tc_res.get("last_modified_file", sub_last_mod)
                            sub_last_bak = tc_res.get("last_backup_file", sub_last_bak)
                            
                            sub_messages.append({"role": "tool", "tool_call_id": getattr(tc, "id", "unknown_id"), "name": tc_name, "content": tc_result_str})

                            short_res = tc_result_str[:150].replace('\n', ' ')
                            if len(tc_result_str) > 150: short_res += "..."
                            trace_entry = f"{len(execution_trace)+1}. **{tc_name}**: "
                            trace_entry += f"-> Результат: {short_res}"
                            execution_trace.append(trace_entry)
                            
                            if tc_name == "finish_task":
                                sub_result = tc_args.get("final_report", tc_result_str)
                                is_sub_finished = True
                                abort_chain = True
                                break
                                
                            if tc_res.get("abort_subsequent_tools"):
                                abort_chain = True
                                
                        if abort_chain:
                            break
                        
                    else:
                        sub_result = sub_msg.content or ""
                        is_sub_finished = True
                        short_res = sub_result[:150].replace('\n', ' ')
                        if len(sub_result) > 150: short_res += "..."
                        execution_trace.append(f"{len(execution_trace)+1}. **Ответ текстом**: -> {short_res}")
                        break
                        
                if not is_sub_finished and not llm_failed:
                    sub_result = "Превышен лимит шагов (20) субагента без вызова finish_task. Работа прервана."

                res["last_modified_file"] = sub_last_mod
                res["last_backup_file"] = sub_last_bak
                
                trace_str = "\n".join(execution_trace) if execution_trace else "Нет шагов"
                res["result_str"] = f"Отчет от субагента '{agent_target}':\n{sub_result}\n\n*--- Трассировка выполнения ---*\n{trace_str}"

    elif f_name == "github_sync":
        action = args.get("action")
        project_id = args.get("project_id")
        commit_message = args.get("commit_message", "Автоматический коммит RITA")
        branch = args.get("branch", "")
        
        if not project_id:
            res["result_str"] = "Укажите project_id."
        else:
            github_token = None
            if user_id:
                with get_db() as conn:
                    with conn.cursor() as c:
                        c.execute("SELECT github_token FROM user_settings WHERE user_id = %s", (user_id,))
                        row = c.fetchone()
                        if row and row[0]: 
                            github_token = row[0]

            if not github_token:
                res["result_str"] = "В настройках не указан GitHub Token (PAT). Добавьте его для работы с приватными репозиториями."
            else:
                with get_db() as conn:
                    with conn.cursor() as c:
                        c.execute("SELECT folder_name, settings FROM projects WHERE id = %s AND user_id = %s", (project_id, user_id))
                        p_row = c.fetchone()
                
                if not p_row:
                    res["result_str"] = f"Проект с ID {project_id} не найден."
                else:
                    p_folder, p_settings_raw = p_row
                    try:
                        p_settings = json.loads(p_settings_raw) if isinstance(p_settings_raw, str) else (p_settings_raw or {})
                    except:
                        p_settings = {}
                        
                    github_repo = p_settings.get("github_repo", "").strip()
                    if not github_repo:
                        res["result_str"] = "В настройках проекта не указан 'github_repo' (формат: user/repo)"
                    else:
                        if not branch:
                            branch = p_settings.get("default_branch", "main")
                            
                        target_work_dir = _resolve_path(p_folder if p_folder else work_dir, work_dir, user_id)
                        os.makedirs(target_work_dir, exist_ok=True)
                        
                        safe_repo_url = f"https://{github_token}@github.com/{github_repo}.git"
                        
                        cmds = []
                        if action == "clone_or_pull":
                            if os.path.exists(os.path.join(target_work_dir, ".git")):
                                cmds.append(f"git checkout {branch} || git checkout -b {branch}")
                                cmds.append(f"git pull origin {branch}")
                            else:
                                cmds.append(f"git clone -b {branch} {safe_repo_url} . || git clone {safe_repo_url} .")
                        elif action == "push":
                            cmds.append('git config user.name "RITA AI Agent"')
                            cmds.append('git config user.email "agent@rita.local"')
                            cmds.append("git add .")
                            cmds.append(f'git commit -m "{commit_message}"')
                            cmds.append(f"git push {safe_repo_url} HEAD:{branch}")
                        else:
                            res["result_str"] = f"Неизвестное действие '{action}'"
                            
                        if cmds:
                            full_cmd = " && ".join(cmds)
                            
                            raw_tool_result_str = await _call_tool_node("/api/terminal/run", {"command": full_cmd, "work_dir": target_work_dir, "user_id": user_id})
                            try:
                                res_data = json.loads(raw_tool_result_str)
                                if isinstance(res_data, dict) and "output" in res_data:
                                    res["result_str"] = res_data["output"]
                                else:
                                    res["result_str"] = raw_tool_result_str
                            except:
                                res["result_str"] = raw_tool_result_str
                                
                            if res["result_str"]:
                                res["result_str"] = res["result_str"].replace(github_token, "***GITHUB_TOKEN***")

                            if not res["result_str"] or res["result_str"].strip() == "":
                                res["result_str"] = "Команда Git выполнена, но вывод пустой."

    elif f_name == "summarize_text":
        text_to_process = args.get("text", "")
        file_path = args.get("file_path", "")

        if text_to_process and len(text_to_process) < 255 and ("/" in text_to_process or "\\" in text_to_process):
            resolved_check = _resolve_path(text_to_process, work_dir, user_id)
            if os.path.isfile(resolved_check):
                file_path = text_to_process
                text_to_process = ""

        if file_path:
            resolved_txt_path = _resolve_path(file_path, work_dir, user_id)
            if os.path.isfile(resolved_txt_path):
                try:
                    with open(resolved_txt_path, "r", encoding="utf-8") as f:
                        text_to_process = f.read()
                except Exception as e:
                    pass

        format_req = args.get("format", "Сводка")
        sys_prompt = f"Сделай суммаризацию текста. Формат: {format_req}. Отвечай только выжимкой, без лишних вступлений."
        messages = [{"role": "user", "content": text_to_process[:25000]}]

        try:
            resp = await generate_response(messages, system_prompt=sys_prompt, model_override=None, agent_name="Summarizer", user_id=user_id, task_id=task_id)
            if resp and resp.choices:
                res["result_str"] = resp.choices[0].message.content.strip()
                
                output_file = args.get("output_file", "")
                if output_file:
                    out_path = _resolve_path(output_file, work_dir, user_id)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(res["result_str"])
                    res["result_str"] = f"Результат сохранен в файл: {out_path}"
            else:
                res["result_str"] = "Ошибка вызова LLM для суммаризации."
        except Exception as e:
            res["result_str"] = f"Ошибка LLM: {e}"

    elif f_name == "finish_task":
        res["result_str"] = args.get("final_report", "Задача завершена.")
        res["abort_subsequent_tools"] = True
        
    return res
