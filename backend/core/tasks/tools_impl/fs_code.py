# backend/core/tasks/tools_impl/fs_code.py
import os
import shutil
import datetime
import time
import re
import difflib
import urllib.parse
from backend.core.tasks.tools_impl.utils import _resolve_path

async def execute_fs_code_tool(f_name: str, args: dict, work_dir: str, last_modified_file: str, last_backup_file: str, agent_id: int, user_id: int, task_id: int, tool_call_id: str, tool_settings: dict) -> dict:
    res = {
        "endpoint": None, "payload": {}, "result_str": "",
        "file_path": None, "abort_subsequent_tools": False,
        "last_modified_file": last_modified_file, "last_backup_file": last_backup_file
    }

    if f_name == "read_file":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        res["file_path"] = file_path
        res["endpoint"], res["payload"] = "/api/fs/read", {"path": file_path, "user_id": user_id}
        
    elif f_name == "check_file_exists":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                res["result_str"] = f"Файл существует: {file_path} (Размер: {size} байт)"
            else:
                res["result_str"] = f"Директория существует: {file_path}"
        else:
            res["result_str"] = f"Не найдено: {file_path}"

    elif f_name == "write_file":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        res["file_path"] = file_path
        if file_path and os.path.exists(file_path):
            try:
                base_dir = work_dir if work_dir else os.path.dirname(os.path.abspath(file_path))
                backup_dir = os.path.join(base_dir, ".backups")
                try:
                    rel_path = os.path.relpath(file_path, base_dir)
                    if rel_path.startswith(".."): rel_path = os.path.basename(file_path)
                except ValueError:
                    rel_path = os.path.basename(file_path)
                    
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.basename(rel_path)
                name, ext = os.path.splitext(filename)
                bak_filename = f"{name}_{timestamp}{ext}"
                
                bak_rel_path = os.path.join(os.path.dirname(rel_path), bak_filename)
                bak_path = os.path.join(backup_dir, bak_rel_path)
                
                os.makedirs(os.path.dirname(bak_path), exist_ok=True)
                shutil.copy2(file_path, bak_path)
                
                res["last_modified_file"] = file_path
                res["last_backup_file"] = bak_path
            except Exception as e:
                print(f"Ошибка бэкапа: {e}")
                
        res["endpoint"], res["payload"] = "/api/fs/write", {"path": file_path, "content": args.get("content", ""), "user_id": user_id}

    elif f_name == "edit_file":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        res["file_path"] = file_path
        search_string = args.get("search_string", "")
        replace_string = args.get("replace_string", "")
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if search_string in content:
                    base_dir = work_dir if work_dir else os.path.dirname(os.path.abspath(file_path))
                    backup_dir = os.path.join(base_dir, ".backups")
                    try:
                        rel_path = os.path.relpath(file_path, base_dir)
                        if rel_path.startswith(".."): rel_path = os.path.basename(file_path)
                    except ValueError:
                        rel_path = os.path.basename(file_path)
                        
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.basename(rel_path)
                    name, ext = os.path.splitext(filename)
                    bak_filename = f"{name}_{timestamp}{ext}"
                    bak_rel_path = os.path.join(os.path.dirname(rel_path), bak_filename)
                    bak_path = os.path.join(backup_dir, bak_rel_path)
                    
                    os.makedirs(os.path.dirname(bak_path), exist_ok=True)
                    shutil.copy2(file_path, bak_path)
                    res["last_modified_file"] = file_path
                    res["last_backup_file"] = bak_path
                    
                    updated_content = content.replace(search_string, replace_string, 1)
                    res["endpoint"], res["payload"] = "/api/fs/write", {"path": file_path, "content": updated_content, "user_id": user_id}
                else:
                    res["result_str"] = "Точная строка для поиска (search_string) не найдена в файле. Используйте write_file."
                    
            except Exception as e:
                res["result_str"] = f"Ошибка редактирования: {e}"
        else:
            res["result_str"] = f"Файл не найден: {file_path}"

    elif f_name == "create_directory":
        dir_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        try:
            os.makedirs(dir_path, exist_ok=True)
            res["result_str"] = f"Успешно создана директория {dir_path}"
        except Exception as e:
            res["result_str"] = f"Ошибка создания: {e}"
            
    elif f_name == "attach_file":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        safe_url = urllib.parse.quote(file_path)
        res["result_str"] = f"Файл {file_path} прикреплен к диалогу.\n\n[ATTACHMENT](/api/tools/fs/download?path={safe_url})"
        
    elif f_name == "scan_project":
        scan_dir = _resolve_path(args.get("work_dir", work_dir), work_dir, user_id)
        if not scan_dir or not os.path.exists(scan_dir):
            res["result_str"] = "Указанная директория не существует."
        else:
            try:
                ignore_dirs = {'.git', 'node_modules', 'venv', '.backups', '__pycache__', '.venv', 'dist', 'build'}
                tree = []
                for root, dirs, files in os.walk(scan_dir):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    rel_root = os.path.relpath(root, scan_dir)
                    if rel_root == '.': rel_root = ''
                    
                    for f in files:
                        if f.endswith(('.py', '.js', '.ts', '.vue', '.json')):
                            f_path = os.path.join(root, f)
                            rel_path = os.path.join(rel_root, f) if rel_root else f
                            try:
                                with open(f_path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                items = []
                                if f.endswith('.py'):
                                    items = re.findall(r'^\s*(?:def|class)\s+(\w+)', content, re.MULTILINE)
                                elif f.endswith(('.js', '.ts', '.vue')):
                                    items_raw = re.findall(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>|class\s+(\w+))', content)
                                    items = [i for tup in items_raw for i in tup if i]
                                    
                                imports = re.findall(r'^(?:import|from)\s+.*', content, re.MULTILINE)
                                
                                tree.append(f"Файл: {rel_path}")
                                if imports:
                                    tree.append("  Импорты: " + ", ".join(imports[:5]) + (f" ... (еще {len(imports)-5})" if len(imports)>5 else ""))
                                if items:
                                    tree.append("  Структура: " + ", ".join(items[:15]) + (f" ... (еще {len(items)-15})" if len(items)>15 else ""))
                            except Exception:
                                tree.append(f"Файл: {rel_path} (ошибка чтения)")
                res["result_str"] = "Сводка по проекту:\n" + "\n".join(tree)
            except Exception as e:
                res["result_str"] = f"Ошибка сканирования: {e}"

    elif f_name == "restore_backup":
        try:
            time_minutes = int(args.get("time_minutes", 60))
            cutoff_time = time.time() - (time_minutes * 60)
            
            base_dir = _resolve_path(work_dir, work_dir, user_id)
            backup_dir = os.path.join(base_dir, ".backups")
            
            if not os.path.exists(backup_dir):
                res["result_str"] = "Папка .backups пуста или отсутствует."
            else:
                backups_by_orig = {}
                for root, dirs, files in os.walk(backup_dir):
                    for f in files:
                        match = re.search(r'_(\d{8}_\d{6})(\.[a-zA-Z0-9]+)?$', f)
                        if match:
                            dt_str = match.group(1)
                            try:
                                dt = datetime.datetime.strptime(dt_str, "%Y%m%d_%H%M%S")
                                ts = dt.timestamp()
                                if ts >= cutoff_time:
                                    bak_path = os.path.join(root, f)
                                    rel_root = os.path.relpath(root, backup_dir)
                                    if rel_root == '.': rel_root = ''
                                    
                                    orig_name = f[:match.start()] + (match.group(2) or "")
                                    orig_path = os.path.normpath(os.path.join(base_dir, rel_root, orig_name))
                                    
                                    if orig_path not in backups_by_orig:
                                        backups_by_orig[orig_path] = []
                                    backups_by_orig[orig_path].append((ts, bak_path))
                            except Exception:
                                pass
                                
                restored_files = []
                for orig_path, baks in backups_by_orig.items():
                    baks.sort(key=lambda x: x[0])
                    oldest_bak_path = baks[0][1]
                    os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                    shutil.copy2(oldest_bak_path, orig_path)
                    restored_files.append(orig_path)
                    
                if restored_files:
                    res["result_str"] = f"Успешно восстановлены файлы (в состоянии на {time_minutes} мин назад):\n" + "\n".join(restored_files)
                else:
                    res["result_str"] = f"За последние {time_minutes} минут бэкапов не найдено."
        except Exception as e:
            res["result_str"] = f"Ошибка восстановления: {e}"

    elif f_name == "check_syntax":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            res["endpoint"], res["payload"] = "/api/terminal/run", {"command": f"python -m py_compile {file_path}", "work_dir": work_dir, "user_id": user_id}
        elif ext in ['.js', '.ts', '.vue']:
            res["endpoint"], res["payload"] = "/api/terminal/run", {"command": f"node --check {file_path}", "work_dir": work_dir, "user_id": user_id}
        else:
            res["result_str"] = f"Синтаксис проверяется только для .py, .js, .ts. Расширение {ext} не поддерживается."
            
    elif f_name == "install_dependencies":
        manager = args.get("manager", "").lower()
        packages = args.get("packages", "")
        t_work_dir = _resolve_path(args.get("work_dir", work_dir), work_dir, user_id)
        
        if manager == "pip":
            cmd = "python3 -m venv .venv && .venv/bin/pip install " + (packages if packages else "-r requirements.txt")
            res["endpoint"], res["payload"] = "/api/terminal/run", {"command": cmd, "work_dir": t_work_dir, "user_id": user_id}
        elif manager == "npm":
            cmd = f"npm install {packages}"
            res["endpoint"], res["payload"] = "/api/terminal/run", {"command": cmd, "work_dir": t_work_dir, "user_id": user_id}
        else:
            res["result_str"] = f"Неизвестный менеджер {manager}. Поддерживаются pip, npm."

    elif f_name == "view_file_diff":
        file_path = _resolve_path(args.get("path", ""), work_dir, user_id)
        if not os.path.exists(file_path):
            res["result_str"] = f"Файл {file_path} не найден."
        else:
            base_dir = _resolve_path(work_dir, work_dir, user_id)
            backup_dir = os.path.join(base_dir, ".backups")
            
            try:
                rel_path = os.path.relpath(file_path, base_dir)
                if rel_path.startswith(".."): rel_path = os.path.basename(file_path)
            except ValueError:
                rel_path = os.path.basename(file_path)
                
            orig_dir = os.path.dirname(rel_path)
            filename = os.path.basename(rel_path)
            name, ext = os.path.splitext(filename)
            
            search_dir = os.path.join(backup_dir, orig_dir)
            if not os.path.exists(search_dir):
                res["result_str"] = f"Бэкапов для {file_path} не найдено."
            else:
                baks = [f for f in os.listdir(search_dir) if f.startswith(name + "_") and f.endswith(ext)]
                if not baks:
                    res["result_str"] = f"Бэкапов для {file_path} не найдено."
                else:
                    baks.sort(reverse=True)
                    latest_bak = os.path.join(search_dir, baks[0])
                    
                    try:
                        with open(latest_bak, 'r', encoding='utf-8') as f1, open(file_path, 'r', encoding='utf-8') as f2:
                            lines1 = f1.readlines()
                            lines2 = f2.readlines()
                            
                        diff = list(difflib.unified_diff(lines1, lines2, fromfile='Backup', tofile='Current', n=3))
                        if diff:
                            res["result_str"] = "```diff\n" + "".join(diff) + "\n```"
                        else:
                            res["result_str"] = "Различий с последним бэкапом не найдено."
                    except Exception as e:
                        res["result_str"] = f"Ошибка генерации diff: {e}"

    return res
