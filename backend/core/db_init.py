# backend/core/db_init.py
import json
import os
import uuid
from backend.core.database import get_db, init_db_pool

def init_db():
    # --- ОЧИСТКА TOOLS.JSON (Удаление rationale) ---
    try:
        tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tools/tools.json'))
        if os.path.exists(tools_path):
            with open(tools_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [line for line in content.split('\n') if not line.strip().startswith('#') and not line.strip().startswith('//')]
                tools_data = json.loads('\n'.join(lines))
            
            changed = False
            for t in tools_data:
                func = t.get("schema_json", {}).get("function", {})
                params = func.get("parameters", {})
                
                if "properties" in params and "rationale" in params["properties"]:
                    del params["properties"]["rationale"]
                    changed = True
                if "required" in params and "rationale" in params["required"]:
                    params["required"].remove("rationale")
                    changed = True
                
            if changed:
                with open(tools_path, 'w', encoding='utf-8') as f:
                    json.dump(tools_data, f, ensure_ascii=False, indent=4)
                print("Успешно удален 'rationale' из tools.json!")
    except Exception as e:
        print(f"Ошибка очистки tools.json: {e}")
    # ---------------------------------------------------------

    init_db_pool()
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                user_name VARCHAR DEFAULT '',
                weather_city VARCHAR DEFAULT '',
                avatar TEXT DEFAULT NULL,
                timezone VARCHAR DEFAULT 'Europe/Moscow',
                github_token VARCHAR DEFAULT NULL
            )''')
            
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_settings' AND column_name='avatar'")
            if not c.fetchone():
                c.execute("ALTER TABLE user_settings ADD COLUMN avatar TEXT DEFAULT NULL")
                
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_settings' AND column_name='timezone'")
            if not c.fetchone():
                c.execute("ALTER TABLE user_settings ADD COLUMN timezone VARCHAR DEFAULT 'Europe/Moscow'")

            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_settings' AND column_name='github_token'")
            if not c.fetchone():
                c.execute("ALTER TABLE user_settings ADD COLUMN github_token VARCHAR DEFAULT NULL")

            c.execute('''CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR NOT NULL,
                description TEXT,
                folder_name VARCHAR NOT NULL,
                settings JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='projects' AND column_name='webhook_token'")
            if not c.fetchone():
                c.execute("ALTER TABLE projects ADD COLUMN webhook_token VARCHAR UNIQUE DEFAULT NULL")
                c.execute("SELECT id FROM projects WHERE webhook_token IS NULL")
                projects_ids = c.fetchall()
                for (p_id,) in projects_ids:
                    c.execute("UPDATE projects SET webhook_token = %s WHERE id = %s", (str(uuid.uuid4()), p_id))

            c.execute('''CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR,
                api_key VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS agents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR,
                description TEXT,
                model VARCHAR,
                system_prompt TEXT,
                skills JSONB DEFAULT '{}',
                tools JSONB DEFAULT '[]',
                is_default INTEGER DEFAULT 0,
                is_main INTEGER DEFAULT 0,
                avatar TEXT,
                profession VARCHAR DEFAULT '',
                settings JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS tools (
                id SERIAL PRIMARY KEY,
                name VARCHAR UNIQUE,
                description TEXT,
                category VARCHAR,
                schema_json JSONB,
                settings JSONB DEFAULT '{}',
                is_active INTEGER DEFAULT 1,
                requires_approval INTEGER DEFAULT 0
            )''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_tools (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR,
                description TEXT,
                category VARCHAR,
                schema_json JSONB,
                settings JSONB DEFAULT '{}',
                is_active INTEGER DEFAULT 1,
                requires_approval INTEGER DEFAULT 0,
                UNIQUE (user_id, name)
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR,
                type VARCHAR DEFAULT 'standard',
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                status VARCHAR,
                current_phase VARCHAR DEFAULT 'discovery',
                target_action VARCHAR DEFAULT 'full_execution',
                agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
                is_cancelled INTEGER DEFAULT 0,
                work_dir TEXT DEFAULT '',
                auto_approve_tools INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Миграции для старых БД (добавление новых колонок для пошагового режима)
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='type'")
            if not c.fetchone():
                c.execute("ALTER TABLE tasks ADD COLUMN type VARCHAR DEFAULT 'standard'")
                
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='current_phase'")
            if not c.fetchone():
                c.execute("ALTER TABLE tasks ADD COLUMN current_phase VARCHAR DEFAULT 'discovery'")
                
            c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tasks' AND column_name='target_action'")
            if not c.fetchone():
                c.execute("ALTER TABLE tasks ADD COLUMN target_action VARCHAR DEFAULT 'full_execution'")

            c.execute('''CREATE TABLE IF NOT EXISTS task_logs (
                id SERIAL PRIMARY KEY,
                task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
                role VARCHAR,
                content TEXT,
                agent_name VARCHAR,
                tool_call_id VARCHAR,
                pending_approval INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS task_agents (
                task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
                agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
                role_in_task VARCHAR,
                PRIMARY KEY (task_id, agent_id)
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS llm_statistics (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR,
                key_id INTEGER,
                model VARCHAR,
                tokens INTEGER,
                agent_name VARCHAR DEFAULT NULL,
                cost FLOAT DEFAULT 0.0,
                task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

        conn.commit()

def create_system_agents_if_needed(user_id: int):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT COUNT(*) FROM agents WHERE user_id = %s', (user_id,))
            if c.fetchone()[0] == 0:
                rita_prompt = """Вы системный агент RITA (Supervisor)."""
                c.execute('''INSERT INTO agents (user_id, name, profession, description, model, system_prompt, skills, is_default, is_main, settings)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                          (user_id, "РИТА", "Управляющий ИИ", "Главный системный агент", None, rita_prompt, "{}", 1, 1, "{}"))
        conn.commit()

def reset_running_tasks():
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("UPDATE tasks SET status = 'failed' WHERE status = 'running'")
        conn.commit()
