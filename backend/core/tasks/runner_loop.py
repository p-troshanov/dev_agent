# backend/core/tasks/runner_loop.py
import json
import asyncio
import time
import os
import traceback
from datetime import datetime

from backend.core.llm import generate_response
from backend.core.state import state
from backend.core.tasks.tool_handlers import handle_tool_call
from backend.core.tasks.runner_db import log_task_action, update_task_status, is_task_cancelled

BASE_WORKSPACE = os.getenv("WORKSPACE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../workspace")))

async def run_task_loop(
    task_id: int, user_id: int, messages: list, sys_prompt: str,
    agent_name: str, agent_model: str, agent_settings: dict, 
    work_dir: str, active_tools_schemas: list, agent_id: int
):
    MAX_ITERATIONS = 20
    last_modified_file = None
    last_backup_file = None
    recent_actions = []
    
    consecutive_tool_errors = 0
    last_tool_error_name = ""
    last_tool_error_msg = ""
    
    base_user_dir = os.path.abspath(os.path.join(BASE_WORKSPACE, f"user_{user_id}"))
    
    # --- Логирование старта ---
    print(f"\n[RUNNER LOOP] Старт задачи ID: {task_id} (Агент: {agent_name}, Модель: {agent_model})", flush=True)
    
    for i in range(MAX_ITERATIONS):
        print(f"\n[RUNNER LOOP] --- Итерация {i+1}/{MAX_ITERATIONS} ---", flush=True)
        
        if is_task_cancelled(task_id):
            print(f"[RUNNER LOOP] Задача {task_id} отменена.", flush=True)
            log_task_action(task_id, "system", "Задача была отменена.", "Система")
            update_task_status(task_id, 'failed')
            break
            
        for idx, m in enumerate(messages):
            content_str = m.get("content", "")
            if not isinstance(content_str, str):
                continue
                
            is_target_tool = False
            if m.get("role") == "tool" and m.get("name") in ["read_file", "scan_project"]:
                is_target_tool = True
            elif m.get("role") == "user" and ("(read_file)" in content_str or "(scan_project)" in content_str):
                is_target_tool = True
                
            if is_target_tool and len(content_str) > 1500:
                is_old = any(future_m.get("role") == "assistant" for future_m in messages[idx+1:])
                if is_old:
                    m["content"] = "[Содержимое скрыто из-за экономии токенов...]"

        kwargs = {"system_prompt": sys_prompt, "agent_name": agent_name, "model_override": agent_model, "user_id": user_id, "task_id": task_id}
        if agent_settings:
            kwargs.update(agent_settings)
            
        if active_tools_schemas:
            formatted_tools = [s if "type" in s else {"type": "function", "function": s} for s in active_tools_schemas]
            kwargs["tools"] = formatted_tools

        debug_dir = os.path.join(base_user_dir, ".debug", f"task_{task_id}")
        os.makedirs(debug_dir, exist_ok=True)
        
        payload_to_save = {
            "messages": messages,
            "system_prompt": sys_prompt,
            "agent_name": agent_name,
            "model_override": agent_model,
        }
        if active_tools_schemas:
            payload_to_save["tools"] = kwargs.get("tools", [])
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        debug_file_path = os.path.join(debug_dir, f"step_{i}_{timestamp}.json")
        try:
            with open(debug_file_path, "w", encoding="utf-8") as f:
                json.dump(payload_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения debug-файла: {e}")

        print(f"[RUNNER LOOP] Вызов LLM...", flush=True)
        response = await generate_response(messages, **kwargs)
        
        if not response or not response.choices:
            print(f"[RUNNER LOOP] Пустой ответ LLM (Rate Limit или ошибка API).", flush=True)
            log_task_action(task_id, "assistant", "Ошибка при обращении к LLM (Rate Limit или ошибка API).", agent_name)
            update_task_status(task_id, 'failed')
            break
            
        message = response.choices[0].message
        
        msg_sig = {
            "content": message.content,
            "tools": [{"name": tc.function.name, "args": tc.function.arguments} for tc in (message.tool_calls or [])] if hasattr(message, 'tool_calls') and message.tool_calls else []
        }
        recent_actions.append(msg_sig)
        if len(recent_actions) > 3:
            recent_actions.pop(0)
            
        if len(recent_actions) == 3 and recent_actions[0] == recent_actions[1] == recent_actions[2]:
            print(f"[RUNNER LOOP] Зацикливание LLM! Переход в ручной режим.", flush=True)
            update_task_status(task_id, 'waiting_user')
            await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
            
            warning_msg = "Зафиксировано зацикливание агента (одни и те же действия 3 раза подряд). Пожалуйста, направьте агента."
            fake_tc_id = f"loop_guard_{int(time.time())}"
            log_task_action(task_id, "tool", warning_msg, "Система (Защита)", fake_tc_id, pending_approval=1)
            
            future = asyncio.Future()
            state.pending_task_tools[fake_tc_id] = future
            
            try:
                approved = await future
            finally:
                if fake_tc_id in state.pending_task_tools:
                    del state.pending_task_tools[fake_tc_id]
                    
            if not approved:
                print(f"[RUNNER LOOP] Прервано пользователем.", flush=True)
                log_task_action(task_id, "system", "Выполнение прервано.", "Система")
                update_task_status(task_id, 'failed')
                await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
                break
            else:
                reminder = f"[{datetime.now().strftime('%H:%M:%S')}] [Пользователь скорректировал задачу]:\n{approved}"
                log_task_action(task_id, "system", reminder, "Система")
                messages.append({"role": "assistant", "content": (message.content or "Ожидаю указаний...")})
                messages.append({"role": "user", "content": reminder})
                
                update_task_status(task_id, 'running')
                await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
                recent_actions.clear()
                continue

        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"[RUNNER LOOP] Получены tool_calls от LLM: {[tc.function.name for tc in message.tool_calls]}", flush=True)
            ts_prefix = f"[{datetime.now().strftime('%H:%M:%S')}] "
            assistant_msg = {"role": "assistant", "content": f"{ts_prefix}{message.content}" if message.content else "", "tool_calls": []}
            
            if message.content and message.content.strip():
                log_task_action(task_id, "assistant", message.content.strip(), agent_name)

            for tc in message.tool_calls:
                assistant_msg["tool_calls"].append({
                    "id": tc.id, "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                })
            messages.append(assistant_msg)
            
            abort_subsequent_tools = [False]
            task_failed_due_to_error_loop = [False]
            
            async def process_single_tc(tc):
                if abort_subsequent_tools[0] or is_task_cancelled(task_id):
                    return tc, "[Выполнение прервано].", False

                f_name = tc.function.name
                try: 
                    args = json.loads(tc.function.arguments)
                    # Если LLM прислал массив или строку вместо словаря — подменяем на пустой dict
                    if not isinstance(args, dict):
                        args = {}
                except: 
                    args = {}

                if f_name in ["finish_task", "message_user"]:
                    is_final = args.get("is_final", False)
                    if f_name == "finish_task" or (is_final and str(is_final).lower() != "false"):
                        return tc, args.get("final_report", args.get("message", "Задача завершена.")), True
                
                print(f"[RUNNER LOOP] Вызов инструмента {f_name} с аргументами: {args}", flush=True)
                
                try:
                    res = await handle_tool_call(
                        f_name, args, work_dir, last_modified_file, last_backup_file,
                        agent_id, user_id, task_id=task_id, tool_call_id=tc.id
                    )
                except Exception as e:
                    print(f"[RUNNER LOOP] Ошибка при выполнении инструмента {f_name}: {e}\n{traceback.format_exc()}", flush=True)
                    res = {"result_str": f"Системная ошибка при выполнении инструмента: {e}", "abort_subsequent_tools": True}
                
                res_str = res.get("result_str", "")
                print(f"[RUNNER LOOP] Результат {f_name}: {res_str[:200]}{'...' if len(res_str) > 200 else ''}", flush=True)
                
                if res.get("abort_subsequent_tools"):
                    abort_subsequent_tools[0] = True

                return tc, res_str, False

            should_exit_runner = False
            for tc in message.tool_calls:
                tc_obj, res_str, is_finish = await process_single_tc(tc)
                if is_finish:
                    log_task_action(task_id, "assistant", res_str, agent_name)
                    update_task_status(task_id, 'completed')
                    should_exit_runner = True
                    break
                else:
                    log_task_action(task_id, "tool", res_str, f"Ответ ({tc_obj.function.name})", tc_obj.id)
                    ts_prefix = f"[{datetime.now().strftime('%H:%M:%S')}] "
                    messages.append({"role": "tool", "tool_call_id": tc_obj.id, "name": tc_obj.function.name, "content": f"{ts_prefix}{res_str}"})
                    
                    is_error = res_str.startswith("Ошибка:") or res_str.startswith("Error:") or "Traceback" in res_str
                    if is_error:
                        if tc_obj.function.name == last_tool_error_name and res_str == last_tool_error_msg:
                            consecutive_tool_errors += 1
                        else:
                            consecutive_tool_errors = 1
                            last_tool_error_name = tc_obj.function.name
                            last_tool_error_msg = res_str
                    else:
                        consecutive_tool_errors = 0
                        last_tool_error_name = ""
                        last_tool_error_msg = ""
                        
                    if consecutive_tool_errors >= 2:
                        error_abort_msg = f"[Системная защита] Инструмент '{tc_obj.function.name}' возвращает одну и ту же ошибку подряд. Выполнение задачи прервано."
                        log_task_action(task_id, "system", error_abort_msg, "Система")
                        update_task_status(task_id, 'failed')
                        task_failed_due_to_error_loop[0] = True
                        break
                        
                # Прерываем цепочку вызовов, если один из инструментов запросил это
                if abort_subsequent_tools[0]:
                    break
                    
            # Если нужно завершить работу агента или сработала защита от зацикливания LLM
            if should_exit_runner or task_failed_due_to_error_loop[0]:
                break
                
        else:
            text_reply = (message.content or "").strip()
            if text_reply:
                print(f"[RUNNER LOOP] Получен ответ LLM без инструментов: {text_reply[:150]}...", flush=True)
                log_task_action(task_id, "assistant", text_reply, agent_name)
                ts_prefix = f"[{datetime.now().strftime('%H:%M:%S')}] "
                messages.append({"role": "assistant", "content": f"{ts_prefix}{text_reply}"})
            
            reminder = f"[{datetime.now().strftime('%H:%M:%S')}] [Система]: Ожидается вызов инструмента. Если задача завершена, используйте 'message_user'!"
            log_task_action(task_id, "system", reminder, "Система")
            messages.append({"role": "user", "content": reminder})
            continue
    else:
        log_task_action(task_id, "system", "Достигнут лимит итераций (20). Задача прервана.", "Система")
        update_task_status(task_id, 'failed')

    print(f"[RUNNER LOOP] Выход из цикла задачи {task_id}.", flush=True)
    await state.broadcast_ws({"type": "TASK_UPDATED", "task_id": task_id}, user_id)
