# backend/core/tools/registry.py
import json
import os
from backend.core.database import get_db

def sync_user_tools(user_id: int):
    """Синхронизирует системные инструменты в персональную таблицу пользователя."""
    print(f"🛠️ [TOOLS REGISTRY] Синхронизация инструментов для пользователя ID: {user_id}...")
    
    tools_file_path = os.path.join(os.path.dirname(__file__), 'tools.json')
    try:
        with open(tools_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Удаляем комментарии, которые могут быть добавлены LLM (например, путь к файлу)
            lines = [line for line in content.split('\n') if not line.strip().startswith('#') and not line.strip().startswith('//')]
            clean_content = '\n'.join(lines)
            tools_registry = json.loads(clean_content)
    except Exception as e:
        print(f"⚠️ Ошибка загрузки tools.json: {e}")
        return

    try:
        with get_db() as conn:
            with conn.cursor() as c:
                for tool in tools_registry:
                    name = tool["name"]
                    # Достаем описание из схемы, так как внешнее поле удалено для чистоты файла
                    description = tool.get("description") or tool.get("schema_json", {}).get("function", {}).get("description", "")
                    category = tool.get("category", "")
                    schema_json_str = json.dumps(tool["schema_json"], ensure_ascii=False)
                    settings_json_str = json.dumps(tool.get("settings", {}), ensure_ascii=False)
                    
                    c.execute("SELECT id FROM user_tools WHERE user_id = %s AND name = %s", (user_id, name))
                    row = c.fetchone()
                    
                    if row is None:
                        c.execute('''INSERT INTO user_tools (user_id, name, description, category, schema_json, settings, is_active, requires_approval) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                                  (user_id, name, description, category, schema_json_str, settings_json_str, 1, 0))
                    else:
                        tool_id = row[0]
                        # Обновляем схему и описание, не затирая пользовательские настройки и аппрувы
                        c.execute('''UPDATE user_tools SET schema_json = %s, description = %s WHERE id = %s AND user_id = %s''', 
                                  (schema_json_str, description, tool_id, user_id))
            
            conn.commit()
    except Exception as e:
        print(f"⚠️ Ошибка при синхронизации инструментов с БД пользователя: {e}")

def sync_tools_to_db():
    """Синхронизирует инструменты для всех уже зарегистрированных пользователей на старте сервера."""
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id FROM users")
                users = c.fetchall()
        for u in users:
            sync_user_tools(u[0])
    except Exception as e:
        print(f"⚠️ Ошибка глобальной синхронизации инструментов: {e}")

