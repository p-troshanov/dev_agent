# ИНСТРУКЦИЯ ДЛЯ ИИ (SYSTEM PROMPT)
Перед тобой актуальная структура проекта и индекс файлов.
Ознакомься со структурой и переходи к выполнению задачи, переданной в промпте.
---
# Структура проекта
```text
📄 _push.bat
📄 _update.bat
📂 backend/
  📂 core/
    📄 auth.py
    📄 config.py
    📄 database.py
    📄 db_init.py
    📄 Dockerfile
    📄 llm.py
    📄 main.py
    📄 schemas.py
    📄 state.py
    📂 agents/
      📄 background.py
      📄 __init__.py
      📂 bg_tasks/
        📄 state.py
    📂 routers/
      📄 agents.py
      📄 auth.py
      📄 keys.py
      📄 projects.py
      📄 settings.py
      📄 tasks.py
      📄 tools.py
      📄 ws.py
    📂 schemas/
      📄 agents.py
      📄 notes.py
      📄 tasks.py
      📄 users.py
      📄 __init__.py
    📂 tasks/
      📄 retriever.py
      📄 runner.py
      📄 runner_context.py
      📄 runner_db.py
      📄 runner_loop.py
      📄 tool_handlers.py
      📂 tools_impl/
        📄 fs_code.py
        📄 system.py
        📄 utils.py
    📂 tools/
      📄 registry.py
      📄 tools.json
  📂 tool_node/
    📄 config.py
    📄 Dockerfile
    📄 main.py
    📄 schemas.py
    📄 state.py
    📄 utils.py
    📂 routers/
      📄 fs.py
      📄 service.py
      📄 terminal.py
📂 frontend/
  📄 Dockerfile
  📄 index.html
  📄 nginx.conf
  📄 README.md
  📄 vite.config.js
  📂 public/
  📂 src/
    📄 App.vue
    📄 main.js
    📂 assets/
      📄 main.css
    📂 components/
      📂 ide/
        📄 IdeModal.vue
      📂 layout/
        📄 MainNav.vue
        📄 Topbar.vue
      📂 plugins/
        📄 AskUserApproval.vue
        📄 CodeApproval.vue
        📄 DefaultApproval.vue
        📄 ImageApproval.vue
        📄 ImageGalleryResult.vue
        📄 SearchImagesApproval.vue
      📂 tasks/
        📄 TaskCreateModal.vue
        📄 TaskLogsArea.vue
        📄 TasksSidebar.vue
    📂 services/
      📄 api.js
    📂 stores/
      📄 appStore.js
    📂 views/
      📄 AgentsView.vue
      📄 AggregatedStatsView.vue
      📄 AuthView.vue
      📄 ProjectsView.vue
      📄 SettingsView.vue
      📄 StatisticsView.vue
      📄 TasksView.vue
      📄 ToolsView.vue
📂 workspace/
  📂 user_1/
    📄 test.txt
    📄 test2.txt
    📂 .debug/
      📂 task_10/
        📄 step_0_20260722_163804.json
        📄 step_0_20260722_164946.json
        📄 step_0_20260722_165628.json
      📂 task_11/
        📄 step_0_20260722_165724.json
        📄 step_0_20260722_165848.json
        📄 step_0_20260722_170023.json
        📄 step_0_20260722_170232.json
        📄 step_1_20260722_165900.json
        📄 step_1_20260722_170035.json
        📄 step_1_20260722_170242.json
        📄 step_2_20260722_165916.json
        📄 step_2_20260722_170122.json
        📄 step_2_20260722_170343.json
        📄 step_3_20260722_170129.json
        📄 step_3_20260722_170356.json
      📂 task_12/
        📄 step_0_20260722_171819.json
        📄 step_1_20260722_171829.json
      📂 task_13/
        📄 step_0_20260722_180704.json
        📄 step_0_20260722_181021.json
      📂 task_14/
        📄 step_0_20260722_181536.json
      📂 task_15/
        📄 step_0_20260722_233009.json
      📂 task_16/
        📄 step_0_20260722_233328.json
        📄 step_1_20260722_233357.json
        📄 step_2_20260722_233400.json
      📂 task_17/
        📄 step_0_20260722_233716.json
        📄 step_1_20260722_233741.json
      📂 task_18/
        📄 step_0_20260722_235020.json
        📄 step_1_20260722_235042.json
      📂 task_19/
        📄 step_0_20260722_235707.json
      📂 task_20/
        📄 step_0_20260723_000049.json
      📂 task_21/
        📄 step_0_20260723_000449.json
      📂 task_22/
        📄 step_0_20260723_000835.json
        📄 step_1_20260723_000848.json
        📄 step_2_20260723_000912.json
        📄 step_3_20260723_000922.json
      📂 task_23/
        📄 step_0_20260723_001508.json
        📄 step_1_20260723_001540.json
        📄 step_2_20260723_001545.json
      📂 task_24/
        📄 step_0_20260723_003159.json
        📄 step_1_20260723_003214.json
        📄 step_2_20260723_003223.json
        📄 step_3_20260723_003247.json
        📄 step_4_20260723_003258.json
        📄 step_5_20260723_003319.json
        📄 step_6_20260723_003327.json
      📂 task_25/
        📄 step_0_20260723_004240.json
        📄 step_1_20260723_004249.json
      📂 task_26/
        📄 step_0_20260723_010122.json
        📄 step_1_20260723_010128.json
        📄 step_2_20260723_010140.json
        📄 step_3_20260723_010207.json
      📂 task_27/
        📄 step_0_20260723_010718.json
        📄 step_10_20260723_010859.json
        📄 step_11_20260723_010904.json
        📄 step_1_20260723_010730.json
        📄 step_2_20260723_010736.json
        📄 step_3_20260723_010750.json
        📄 step_4_20260723_010804.json
        📄 step_5_20260723_010813.json
        📄 step_6_20260723_010818.json
        📄 step_7_20260723_010824.json
        📄 step_8_20260723_010830.json
        📄 step_9_20260723_010846.json
      📂 task_28/
        📄 step_0_20260723_011209.json
        📄 step_1_20260723_011225.json
      📂 task_29/
        📄 step_0_20260723_011656.json
        📄 step_1_20260723_011707.json
        📄 step_2_20260723_011734.json
        📄 step_3_20260723_011751.json
        📄 step_4_20260723_011801.json
        📄 step_5_20260723_011812.json
      📂 task_30/
        📄 step_0_20260723_012120.json
        📄 step_0_20260723_012755.json
        📄 step_1_20260723_012132.json
        📄 step_1_20260723_012811.json
        📄 step_2_20260723_012229.json
        📄 step_2_20260723_012832.json
        📄 step_3_20260723_012240.json
        📄 step_3_20260723_013548.json
        📄 step_4_20260723_012256.json
        📄 step_4_20260723_013602.json
        📄 step_5_20260723_012312.json
        📄 step_5_20260723_013615.json
        📄 step_6_20260723_012319.json
        📄 step_6_20260723_013815.json
        📄 step_7_20260723_012329.json
        📄 step_7_20260723_013845.json
      📂 task_31/
        📄 step_0_20260723_014620.json
        📄 step_10_20260723_015014.json
        📄 step_11_20260723_015108.json
        📄 step_12_20260723_015132.json
        📄 step_13_20260723_015140.json
        📄 step_1_20260723_014640.json
        📄 step_2_20260723_014651.json
        📄 step_3_20260723_014716.json
        📄 step_4_20260723_014720.json
        📄 step_5_20260723_014727.json
        📄 step_6_20260723_014734.json
        📄 step_7_20260723_014745.json
        📄 step_8_20260723_014801.json
        📄 step_9_20260723_014812.json
      📂 task_32/
        📄 step_0_20260723_020844.json
        📄 step_0_20260723_021549.json
        📄 step_10_20260723_021031.json
        📄 step_11_20260723_021040.json
        📄 step_12_20260723_021051.json
        📄 step_13_20260723_021101.json
        📄 step_14_20260723_021110.json
        📄 step_15_20260723_023047.json
        📄 step_16_20260723_023100.json
        📄 step_1_20260723_020856.json
        📄 step_1_20260723_021853.json
        📄 step_2_20260723_020908.json
        📄 step_2_20260723_022709.json
        📄 step_3_20260723_020920.json
        📄 step_4_20260723_020931.json
        📄 step_5_20260723_020943.json
        📄 step_6_20260723_020952.json
        📄 step_7_20260723_021004.json
        📄 step_8_20260723_021011.json
        📄 step_9_20260723_021023.json
      📂 task_33/
        📄 step_0_20260723_023103.json
        📄 step_0_20260723_023441.json
        📄 step_10_20260723_023253.json
        📄 step_10_20260723_023610.json
        📄 step_11_20260723_023304.json
        📄 step_11_20260723_023618.json
        📄 step_12_20260723_023315.json
        📄 step_12_20260723_023626.json
        📄 step_13_20260723_023330.json
        📄 step_13_20260723_023635.json
        📄 step_14_20260723_023340.json
        📄 step_14_20260723_023642.json
        📄 step_15_20260723_023349.json
        📄 step_15_20260723_023651.json
        📄 step_16_20260723_023357.json
        📄 step_16_20260723_023700.json
        📄 step_17_20260723_023405.json
        📄 step_17_20260723_023707.json
        📄 step_18_20260723_023413.json
        📄 step_18_20260723_023718.json
        📄 step_19_20260723_023422.json
        📄 step_19_20260723_023726.json
        📄 step_1_20260723_023109.json
        📄 step_1_20260723_023456.json
        📄 step_2_20260723_023127.json
        📄 step_2_20260723_023504.json
        📄 step_3_20260723_023136.json
        📄 step_3_20260723_023516.json
        📄 step_4_20260723_023146.json
        📄 step_4_20260723_023524.json
        📄 step_5_20260723_023155.json
        📄 step_5_20260723_023530.json
        📄 step_6_20260723_023206.json
        📄 step_6_20260723_023538.json
        📄 step_7_20260723_023216.json
        📄 step_7_20260723_023546.json
        📄 step_8_20260723_023225.json
        📄 step_8_20260723_023553.json
        📄 step_9_20260723_023233.json
        📄 step_9_20260723_023601.json
      📂 task_34/
        📄 step_0_20260723_025416.json
        📄 step_1_20260723_025424.json
        📄 step_2_20260723_025509.json
        📄 step_3_20260723_025516.json
        📄 step_4_20260723_025547.json
      📂 task_4/
        📄 step_0_20260722_151457.json
        📄 step_1_20260722_151509.json
        📄 step_2_20260722_151518.json
      📂 task_5/
        📄 step_0_20260722_152915.json
        📄 step_1_20260722_152948.json
        📄 step_2_20260722_152958.json
        📄 step_3_20260722_153012.json
        📄 step_4_20260722_153034.json
        📄 step_5_20260722_153048.json
        📄 step_6_20260722_153121.json
      📂 task_6/
        📄 step_0_20260722_154125.json
        📄 step_1_20260722_154211.json
      📂 task_7/
        📄 step_0_20260722_161000.json
        📄 step_0_20260722_161207.json
        📄 step_1_20260722_161013.json
        📄 step_1_20260722_161213.json
      📂 task_8/
        📄 step_0_20260722_162811.json
        📄 step_1_20260722_162824.json
      📂 task_9/
        📄 step_0_20260722_163223.json
    📂 dev_agent/
      📄 _push.bat
      📂 backend/
        📂 core/
          📄 auth.py
          📄 config.py
          📄 database.py
          📄 db_init.py
          📄 Dockerfile
          📄 llm.py
          📄 main.py
          📄 schemas.py
          📄 state.py
          📂 agents/
            📄 background.py
            📄 __init__.py
            📂 bg_tasks/
              📄 state.py
          📂 routers/
            📄 agents.py
            📄 auth.py
            📄 keys.py
            📄 projects.py
            📄 settings.py
            📄 tasks.py
            📄 tools.py
            📄 ws.py
          📂 schemas/
            📄 agents.py
            📄 notes.py
            📄 tasks.py
            📄 users.py
            📄 __init__.py
          📂 tasks/
            📄 retriever.py
            📄 runner.py
            📄 runner_context.py
            📄 runner_db.py
            📄 runner_loop.py
            📄 tool_handlers.py
            📂 tools_impl/
              📄 fs_code.py
              📄 system.py
              📄 utils.py
              📄 _inspect_tmp.py
          📂 tools/
            📄 registry.py
            📄 tools.json
        📂 tool_node/
          📄 config.py
          📄 Dockerfile
          📄 main.py
          📄 schemas.py
          📄 state.py
          📄 utils.py
          📂 routers/
            📄 fs.py
            📄 service.py
            📄 terminal.py
      📂 frontend/
        📄 Dockerfile
        📄 index.html
        📄 nginx.conf
        📄 README.md
        📄 vite.config.js
        📂 public/
        📂 src/
          📄 App.vue
          📄 main.js
          📂 assets/
            📄 main.css
          📂 components/
            📂 ide/
              📄 IdeModal.vue
            📂 layout/
              📄 MainNav.vue
              📄 Topbar.vue
            📂 plugins/
              📄 AskUserApproval.vue
              📄 CodeApproval.vue
              📄 DefaultApproval.vue
              📄 ImageApproval.vue
              📄 ImageGalleryResult.vue
              📄 SearchImagesApproval.vue
            📂 tasks/
              📄 TaskCreateModal.vue
              📄 TaskLogsArea.vue
              📄 TasksSidebar.vue
          📂 services/
            📄 api.js
          📂 stores/
            📄 appStore.js
          📂 views/
            📄 AgentsView.vue
            📄 AggregatedStatsView.vue
            📄 AuthView.vue
            📄 ProjectsView.vue
            📄 SettingsView.vue
            📄 StatisticsView.vue
            📄 TasksView.vue
            📄 ToolsView.vue
    📂 test/
      📄 приветствие.txt
  📂 user_2/
```

# Индекс файлов (Пути, Строки, Зависимости, Суть)

- **_push.bat** - *(36 строк)* `[Конфиг / Без сигнатур]`
- **_update.bat** - *(30 строк)* `[Конфиг / Без сигнатур]`
- **backend/core/auth.py** - *(54 строк)* 🔗 Структура: [Def: verify_password, Def: get_password_hash, Def: create_access_token, Def: get_current_user] 🔗 Зависимости: [datetime, typing, jose, bcrypt, fastapi, security] `def verify_password(plain_password | def get_password_hash(password | def create_access_token(data`
- **backend/core/config.py** - *(35 строк)* 🔗 Зависимости: [os, urllib.parse, dotenv] `[Конфиг / Без сигнатур]`
- **backend/core/database.py** - *(84 строк)* 🔗 Структура: [Def: init_db_pool, Def: close_db_pool, Def: get_db] 🔗 Зависимости: [time, psycopg2, pool, contextlib, config] `def init_db_pool() | def close_db_pool() | def get_db()`
- **backend/core/db_init.py** - *(196 строк)* 🔗 Структура: [Def: init_db, Def: create_system_agents_if_needed, Def: reset_running_tasks] 🔗 Зависимости: [json, os, uuid, database] `def init_db()`
- **backend/core/Dockerfile** - *(20 строк)* `[Конфиг / Без сигнатур]`
- **backend/core/llm.py** - *(333 строк)* 🔗 Структура: [Def: get_keys_from_db, Def: log_llm_request, Def: parse_groq_cooldown, Def: _extract_total_tokens, Def: _calculate_cost] 🔗 Зависимости: [os, json, time, re, asyncio, urllib.request] `def get_keys_from_db(provider | def log_llm_request(provider`
- **backend/core/main.py** - *(56 строк)* 🔗 Зависимости: [asyncio, uvicorn, logging, fastapi, cors, database] `async def startup_event() | async def shutdown_event()`
- **backend/core/schemas.py** - *(80 строк)* 🔗 Структура: [Class: UserCreate(), Class: UserLogin(), Class: Token(), Class: UserData(), Class: SettingsUpdate()] 🔗 Зависимости: [pydantic, typing] `class UserCreate(BaseModel) | class UserLogin(BaseModel) | class Token(BaseModel)`
- **backend/core/state.py** - *(37 строк)* 🔗 Структура: [Class: AppState(__init__, add_connection, remove_connection)] `class AppState | def __init__(self) | def add_connection(self, user_id`
- **backend/core/agents/background.py** - *(16 строк)* 🔗 Зависимости: [asyncio, state] `async def start_background_worker(broadcast_cb)`
- **backend/core/agents/__init__.py** - *(1 строк)* `[Конфиг / Без сигнатур]`
- **backend/core/agents/bg_tasks/state.py** - *(13 строк)* 🔗 Структура: [Def: set_broadcast_callback, Def: get_broadcast_callback] 🔗 Зависимости: [asyncio] `def set_broadcast_callback(cb) | def get_broadcast_callback()`
- **backend/core/routers/agents.py** - *(65 строк)* 🔗 Структура: [Def: get_agents, Def: create_agent, Def: update_agent, Def: delete_agent] 🔗 Зависимости: [json, fastapi, database, schemas, auth] `def get_agents(current_user | def create_agent(data | def update_agent(agent_id`
- **backend/core/routers/auth.py** - *(64 строк)* 🔗 Структура: [Def: register_user, Def: login_for_access_token, Def: read_users_me] 🔗 Зависимости: [fastapi, security, database, db_init, auth, schemas] `def register_user(user | def login_for_access_token(form_data`
- **backend/core/routers/keys.py** - *(172 строк)* 🔗 Структура: [Def: get_api_keys, Def: add_api_key, Def: delete_api_key, Def: get_keys_status, Def: get_or_balance_sync] 🔗 Зависимости: [urllib.request, json, asyncio, fastapi, database, schemas] `def get_api_keys(current_user | def add_api_key(data | def delete_api_key(key_id`
- **backend/core/routers/projects.py** - *(79 строк)* 🔗 Структура: [Def: get_projects, Def: create_project, Def: update_project, Def: reset_project_webhook, Def: delete_project] 🔗 Зависимости: [json, uuid, fastapi, database, schemas, auth] `def get_projects(current_user | def create_project(data | def update_project(project_id`
- **backend/core/routers/settings.py** - *(36 строк)* 🔗 Структура: [Def: get_settings, Def: update_settings] 🔗 Зависимости: [json, fastapi, database, schemas, auth, config] `def get_settings(current_user | def update_settings(data`
- **backend/core/routers/tasks.py** - *(312 строк)* 🔗 Структура: [Class: TaskContinue(), Def: get_tasks, Def: get_task_logs, Def: export_task_context, Def: export_task_debug] 🔗 Зависимости: [json, os, zipfile, io, re, fastapi] `class TaskContinue(BaseModel) | def get_tasks(current_user`
- **backend/core/routers/tools.py** - *(225 строк)* 🔗 Структура: [Class: FileRenameRequest(), Def: _get_safe_user_path, Def: get_tools, Def: update_tool, Def: local_read_file] 🔗 Зависимости: [os, json, shutil, re, fastapi, responses] `class FileRenameRequest(BaseModel) | def _get_safe_user_path(path | def get_tools(current_user`
- **backend/core/routers/ws.py** - *(38 строк)* 🔗 Зависимости: [fastapi, jose, config, state] `async def websocket_endpoint(websocket`
- **backend/core/schemas/agents.py** - *(16 строк)* 🔗 Структура: [Class: AgentCreateUpdate()] 🔗 Зависимости: [pydantic, typing] `class AgentCreateUpdate(BaseModel)`
- **backend/core/schemas/notes.py** - *(21 строк)* 🔗 Структура: [Class: NoteCategoryCreateUpdate(), Class: NoteCreateUpdate(), Class: NoteScheduleUpdate()] 🔗 Зависимости: [pydantic, typing] `class NoteCategoryCreateUpdate(BaseModel) | class NoteCreateUpdate(BaseModel) | class NoteScheduleUpdate(BaseModel)`
- **backend/core/schemas/tasks.py** - *(40 строк)* 🔗 Структура: [Class: ProjectCreateUpdate(), Class: TaskCreate(), Class: TaskToolConfirm(), Class: TaskToolResponse(), Class: ToolConfirm()] 🔗 Зависимости: [pydantic, typing] `class ProjectCreateUpdate(BaseModel) | class TaskCreate(BaseModel) | class TaskToolConfirm(BaseModel)`
- **backend/core/schemas/users.py** - *(30 строк)* 🔗 Структура: [Class: UserCreate(), Class: UserLogin(), Class: Token(), Class: UserData(), Class: SettingsUpdate()] 🔗 Зависимости: [pydantic, typing] `class UserCreate(BaseModel) | class UserLogin(BaseModel) | class Token(BaseModel)`
- **backend/core/schemas/__init__.py** - *(5 строк)* 🔗 Зависимости: [users, agents, tasks, notes] `[Конфиг / Без сигнатур]`
- **backend/core/tasks/retriever.py** - *(70 строк)* 🔗 Зависимости: [json, database, llm] `async def get_relevant_tools(task_description`
- **backend/core/tasks/runner.py** - *(116 строк)* 🔗 Зависимости: [json, os, traceback, database, state, runner_db] `async def run_task(task_id`
- **backend/core/tasks/runner_context.py** - *(116 строк)* 🔗 Структура: [Def: setup_task_workspace, Def: build_system_prompt, Def: build_initial_messages, Def: get_active_manager_tools] 🔗 Зависимости: [os, json, re, datetime, database] `def setup_task_workspace(user_id | def build_system_prompt(agent_name`
- **backend/core/tasks/runner_db.py** - *(23 строк)* 🔗 Структура: [Def: log_task_action, Def: update_task_status, Def: is_task_cancelled] 🔗 Зависимости: [database] `def log_task_action(task_id | def update_task_status(task_id | def is_task_cancelled(task_id`
- **backend/core/tasks/runner_loop.py** - *(235 строк)* 🔗 Зависимости: [json, asyncio, time, os, traceback, datetime] `async def run_task_loop(`
- **backend/core/tasks/tool_handlers.py** - *(208 строк)* 🔗 Зависимости: [json, asyncio, os, shutil, database, state] `async def handle_tool_call(f_name`
- **backend/core/tasks/tools_impl/fs_code.py** - *(282 строк)* 🔗 Структура: [Def: _strip_zwsp] 🔗 Зависимости: [os, shutil, datetime, time, re, difflib] `def _strip_zwsp(text | async def execute_fs_code_tool(f_name`
- **backend/core/tasks/tools_impl/system.py** - *(421 строк)* 🔗 Структура: [Def: _strip_zwsp] 🔗 Зависимости: [os, json, time, re, urllib.parse, urllib.request] `def _strip_zwsp(text | async def execute_system_tool(f_name`
- **backend/core/tasks/tools_impl/utils.py** - *(110 строк)* 🔗 Структура: [Def: _hide_host_path, Def: _resolve_path, Def: _call_tool_node_sync] 🔗 Зависимости: [os, json, urllib.request, urllib.error, asyncio, re] `def _hide_host_path(text | def _resolve_path(path`
- **backend/core/tools/registry.py** - *(61 строк)* 🔗 Структура: [Def: sync_user_tools, Def: sync_tools_to_db] 🔗 Зависимости: [json, os, database] `def sync_user_tools(user_id | def sync_tools_to_db()`
- **backend/core/tools/tools.json** - *(585 строк)* `[Конфиг / Без сигнатур]`
- **backend/tool_node/config.py** - *(11 строк)* 🔗 Зависимости: [os] `[Конфиг / Без сигнатур]`
- **backend/tool_node/Dockerfile** - *(26 строк)* `[Конфиг / Без сигнатур]`
- **backend/tool_node/main.py** - *(16 строк)* 🔗 Зависимости: [fastapi, uvicorn, fs, terminal, service] `[Конфиг / Без сигнатур]`
- **backend/tool_node/schemas.py** - *(30 строк)* 🔗 Структура: [Class: FileWritePayload(), Class: FileReadPayload(), Class: CommandPayload(), Class: ServiceStartPayload(), Class: ServiceActionPayload()] 🔗 Зависимости: [pydantic] `class FileWritePayload(BaseModel) | class FileReadPayload(BaseModel) | class CommandPayload(BaseModel)`
- **backend/tool_node/state.py** - *(3 строк)* `[Конфиг / Без сигнатур]`
- **backend/tool_node/utils.py** - *(73 строк)* 🔗 Структура: [Def: get_safe_path, Def: build_sandbox_cmd] 🔗 Зависимости: [os, shutil, re, fastapi, config] `def get_safe_path(relative_path | def build_sandbox_cmd(command`
- **backend/tool_node/routers/fs.py** - *(43 строк)* 🔗 Зависимости: [os, fastapi, schemas, utils] `async def write_file(payload | async def read_file(payload`
- **backend/tool_node/routers/service.py** - *(82 строк)* 🔗 Зависимости: [os, uuid, subprocess, fastapi, schemas, utils] `async def start_service(payload | async def stop_service(payload | async def status_service(payload`
- **backend/tool_node/routers/terminal.py** - *(79 строк)* 🔗 Зависимости: [os, subprocess, fastapi, schemas, utils, config] `async def run_command(payload | def decode_output(b`
- **frontend/Dockerfile** - *(16 строк)* `[Конфиг / Без сигнатур]`
- **frontend/index.html** - *(13 строк)* `[Конфиг / Без сигнатур]`
- **frontend/nginx.conf** - *(49 строк)* `[Конфиг / Без сигнатур]`
- **frontend/README.md** - *(5 строк)* `[Конфиг / Без сигнатур]`
- **frontend/vite.config.js** - *(20 строк)* 🔗 Зависимости: [vite, plugin-vue] `[Конфиг / Без сигнатур]`
- **frontend/src/App.vue** - *(44 строк)* 🔗 Зависимости: [appStore, MainNav, Topbar, IdeModal] `[Конфиг / Без сигнатур]`
- **frontend/src/main.js** - *(42 строк)* 🔗 Зависимости: [App, SettingsView, StatisticsView, AggregatedStatsView, AgentsView, ToolsView] `[Конфиг / Без сигнатур]`
- **frontend/src/assets/main.css** - *(179 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/ide/IdeModal.vue** - *(325 строк)* 🔗 Зависимости: [appStore, api] `[Конфиг / Без сигнатур]`
- **frontend/src/components/layout/MainNav.vue** - *(26 строк)* 🔗 Зависимости: [appStore] `[Конфиг / Без сигнатур]`
- **frontend/src/components/layout/Topbar.vue** - *(32 строк)* 🔗 Зависимости: [appStore] `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/AskUserApproval.vue** - *(53 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/CodeApproval.vue** - *(76 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/DefaultApproval.vue** - *(27 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/ImageApproval.vue** - *(26 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/ImageGalleryResult.vue** - *(92 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/components/plugins/SearchImagesApproval.vue** - *(45 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/tasks/TaskCreateModal.vue** - *(89 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/tasks/TaskLogsArea.vue** - *(448 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/components/tasks/TasksSidebar.vue** - *(85 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/services/api.js** - *(159 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/stores/appStore.js** - *(78 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/views/AgentsView.vue** - *(435 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/views/AggregatedStatsView.vue** - *(125 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/views/AuthView.vue** - *(168 строк)* 🔗 Зависимости: [api, appStore] `[Конфиг / Без сигнатур]`
- **frontend/src/views/ProjectsView.vue** - *(245 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/views/SettingsView.vue** - *(273 строк)* `[Конфиг / Без сигнатур]`
- **frontend/src/views/StatisticsView.vue** - *(106 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **frontend/src/views/TasksView.vue** - *(217 строк)* 🔗 Зависимости: [api, appStore, TasksSidebar, TaskLogsArea, TaskCreateModal] `[Конфиг / Без сигнатур]`
- **frontend/src/views/ToolsView.vue** - *(253 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/test.txt** - *(1 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/test2.txt** - *(4 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_10/step_0_20260722_163804.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_10/step_0_20260722_164946.json** - *(432 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_10/step_0_20260722_165628.json** - *(440 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_0_20260722_165724.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_0_20260722_165848.json** - *(432 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_0_20260722_170023.json** - *(448 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_0_20260722_170232.json** - *(472 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_1_20260722_165900.json** - *(452 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_1_20260722_170035.json** - *(456 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_1_20260722_170242.json** - *(480 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_2_20260722_165916.json** - *(460 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_2_20260722_170122.json** - *(476 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_2_20260722_170343.json** - *(500 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_3_20260722_170129.json** - *(496 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_11/step_3_20260722_170356.json** - *(520 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_12/step_0_20260722_171819.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_12/step_1_20260722_171829.json** - *(440 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_13/step_0_20260722_180704.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_13/step_0_20260722_181021.json** - *(401 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_14/step_0_20260722_181536.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_15/step_0_20260722_233009.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_16/step_0_20260722_233328.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_16/step_1_20260722_233357.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_16/step_2_20260722_233400.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_17/step_0_20260722_233716.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_17/step_1_20260722_233741.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_18/step_0_20260722_235020.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_18/step_1_20260722_235042.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_19/step_0_20260722_235707.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_20/step_0_20260723_000049.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_21/step_0_20260723_000449.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_22/step_0_20260723_000835.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_22/step_1_20260723_000848.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_22/step_2_20260723_000912.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_22/step_3_20260723_000922.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_23/step_0_20260723_001508.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_23/step_1_20260723_001540.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_23/step_2_20260723_001545.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_0_20260723_003159.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_1_20260723_003214.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_2_20260723_003223.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_3_20260723_003247.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_4_20260723_003258.json** - *(469 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_5_20260723_003319.json** - *(489 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_24/step_6_20260723_003327.json** - *(509 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_25/step_0_20260723_004240.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_25/step_1_20260723_004249.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_26/step_0_20260723_010122.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_26/step_1_20260723_010128.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_26/step_2_20260723_010140.json** - *(443 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_26/step_3_20260723_010207.json** - *(505 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_0_20260723_010718.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_10_20260723_010859.json** - *(589 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_11_20260723_010904.json** - *(609 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_1_20260723_010730.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_2_20260723_010736.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_3_20260723_010750.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_4_20260723_010804.json** - *(469 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_5_20260723_010813.json** - *(489 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_6_20260723_010818.json** - *(509 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_7_20260723_010824.json** - *(529 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_8_20260723_010830.json** - *(549 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_27/step_9_20260723_010846.json** - *(569 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_28/step_0_20260723_011209.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_28/step_1_20260723_011225.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_0_20260723_011656.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_1_20260723_011707.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_2_20260723_011734.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_3_20260723_011751.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_4_20260723_011801.json** - *(469 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_29/step_5_20260723_011812.json** - *(489 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_0_20260723_012120.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_0_20260723_012755.json** - *(465 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_1_20260723_012132.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_1_20260723_012811.json** - *(485 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_2_20260723_012229.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_2_20260723_012832.json** - *(547 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_3_20260723_012240.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_3_20260723_013548.json** - *(567 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_4_20260723_012256.json** - *(469 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_4_20260723_013602.json** - *(587 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_5_20260723_012312.json** - *(489 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_5_20260723_013615.json** - *(607 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_6_20260723_012319.json** - *(509 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_6_20260723_013815.json** - *(627 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_7_20260723_012329.json** - *(529 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_30/step_7_20260723_013845.json** - *(647 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_0_20260723_014620.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_10_20260723_015014.json** - *(631 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_11_20260723_015108.json** - *(651 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_12_20260723_015132.json** - *(671 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_13_20260723_015140.json** - *(691 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_1_20260723_014640.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_2_20260723_014651.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_3_20260723_014716.json** - *(477 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_4_20260723_014720.json** - *(497 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_5_20260723_014727.json** - *(517 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_6_20260723_014734.json** - *(537 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_7_20260723_014745.json** - *(557 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_8_20260723_014801.json** - *(577 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_31/step_9_20260723_014812.json** - *(611 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_0_20260723_020844.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_0_20260723_021549.json** - *(521 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_10_20260723_021031.json** - *(631 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_11_20260723_021040.json** - *(651 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_12_20260723_021051.json** - *(685 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_13_20260723_021101.json** - *(705 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_14_20260723_021110.json** - *(725 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_15_20260723_023047.json** - *(733 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_16_20260723_023100.json** - *(741 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_1_20260723_020856.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_1_20260723_021853.json** - *(529 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_2_20260723_020908.json** - *(443 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_2_20260723_022709.json** - *(549 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_3_20260723_020920.json** - *(477 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_4_20260723_020931.json** - *(497 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_5_20260723_020943.json** - *(517 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_6_20260723_020952.json** - *(537 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_7_20260723_021004.json** - *(557 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_8_20260723_021011.json** - *(577 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_32/step_9_20260723_021023.json** - *(611 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_0_20260723_023103.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_0_20260723_023441.json** - *(521 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_10_20260723_023253.json** - *(687 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_10_20260723_023610.json** - *(721 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_11_20260723_023304.json** - *(707 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_11_20260723_023618.json** - *(741 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_12_20260723_023315.json** - *(727 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_12_20260723_023626.json** - *(761 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_13_20260723_023330.json** - *(747 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_13_20260723_023635.json** - *(781 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_14_20260723_023340.json** - *(767 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_14_20260723_023642.json** - *(801 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_15_20260723_023349.json** - *(787 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_15_20260723_023651.json** - *(821 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_16_20260723_023357.json** - *(807 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_16_20260723_023700.json** - *(841 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_17_20260723_023405.json** - *(827 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_17_20260723_023707.json** - *(861 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_18_20260723_023413.json** - *(847 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_18_20260723_023718.json** - *(881 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_19_20260723_023422.json** - *(867 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_19_20260723_023726.json** - *(901 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_1_20260723_023109.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_1_20260723_023456.json** - *(541 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_2_20260723_023127.json** - *(471 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_2_20260723_023504.json** - *(561 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_3_20260723_023136.json** - *(505 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_3_20260723_023516.json** - *(581 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_4_20260723_023146.json** - *(539 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_4_20260723_023524.json** - *(601 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_5_20260723_023155.json** - *(573 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_5_20260723_023530.json** - *(621 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_6_20260723_023206.json** - *(607 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_6_20260723_023538.json** - *(641 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_7_20260723_023216.json** - *(627 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_7_20260723_023546.json** - *(661 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_8_20260723_023225.json** - *(647 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_8_20260723_023553.json** - *(681 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_9_20260723_023233.json** - *(667 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_33/step_9_20260723_023601.json** - *(701 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_34/step_0_20260723_025416.json** - *(389 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_34/step_1_20260723_025424.json** - *(409 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_34/step_2_20260723_025509.json** - *(429 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_34/step_3_20260723_025516.json** - *(449 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_34/step_4_20260723_025547.json** - *(469 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_4/step_0_20260722_151457.json** - *(525 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_4/step_1_20260722_151509.json** - *(545 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_4/step_2_20260722_151518.json** - *(565 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_0_20260722_152915.json** - *(477 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_1_20260722_152948.json** - *(497 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_2_20260722_152958.json** - *(517 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_3_20260722_153012.json** - *(537 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_4_20260722_153034.json** - *(557 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_5_20260722_153048.json** - *(561 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_5/step_6_20260722_153121.json** - *(581 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_6/step_0_20260722_154125.json** - *(506 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_6/step_1_20260722_154211.json** - *(526 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_7/step_0_20260722_161000.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_7/step_0_20260722_161207.json** - *(436 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_7/step_1_20260722_161013.json** - *(440 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_7/step_1_20260722_161213.json** - *(456 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_8/step_0_20260722_162811.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_8/step_1_20260722_162824.json** - *(440 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/.debug/task_9/step_0_20260722_163223.json** - *(420 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/_push.bat** - *(36 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/auth.py** - *(54 строк)* 🔗 Структура: [Def: verify_password, Def: get_password_hash, Def: create_access_token, Def: get_current_user] 🔗 Зависимости: [datetime, typing, jose, bcrypt, fastapi, security] `def verify_password(plain_password | def get_password_hash(password | def create_access_token(data`
- **workspace/user_1/dev_agent/backend/core/config.py** - *(35 строк)* 🔗 Зависимости: [os, urllib.parse, dotenv] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/database.py** - *(84 строк)* 🔗 Структура: [Def: init_db_pool, Def: close_db_pool, Def: get_db] 🔗 Зависимости: [time, psycopg2, pool, contextlib, config] `def init_db_pool() | def close_db_pool() | def get_db()`
- **workspace/user_1/dev_agent/backend/core/db_init.py** - *(196 строк)* 🔗 Структура: [Def: init_db, Def: create_system_agents_if_needed, Def: reset_running_tasks] 🔗 Зависимости: [json, os, uuid, database] `def init_db()`
- **workspace/user_1/dev_agent/backend/core/Dockerfile** - *(20 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/llm.py** - *(333 строк)* 🔗 Структура: [Def: get_keys_from_db, Def: log_llm_request, Def: parse_groq_cooldown, Def: _extract_total_tokens, Def: _calculate_cost] 🔗 Зависимости: [os, json, time, re, asyncio, urllib.request] `def get_keys_from_db(provider | def log_llm_request(provider`
- **workspace/user_1/dev_agent/backend/core/main.py** - *(56 строк)* 🔗 Зависимости: [asyncio, uvicorn, logging, fastapi, cors, database] `async def startup_event() | async def shutdown_event()`
- **workspace/user_1/dev_agent/backend/core/schemas.py** - *(80 строк)* 🔗 Структура: [Class: UserCreate(), Class: UserLogin(), Class: Token(), Class: UserData(), Class: SettingsUpdate()] 🔗 Зависимости: [pydantic, typing] `class UserCreate(BaseModel) | class UserLogin(BaseModel) | class Token(BaseModel)`
- **workspace/user_1/dev_agent/backend/core/state.py** - *(37 строк)* 🔗 Структура: [Class: AppState(__init__, add_connection, remove_connection)] `class AppState | def __init__(self) | def add_connection(self, user_id`
- **workspace/user_1/dev_agent/backend/core/agents/background.py** - *(16 строк)* 🔗 Зависимости: [asyncio, state] `async def start_background_worker(broadcast_cb)`
- **workspace/user_1/dev_agent/backend/core/agents/__init__.py** - *(1 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/agents/bg_tasks/state.py** - *(13 строк)* 🔗 Структура: [Def: set_broadcast_callback, Def: get_broadcast_callback] 🔗 Зависимости: [asyncio] `def set_broadcast_callback(cb) | def get_broadcast_callback()`
- **workspace/user_1/dev_agent/backend/core/routers/agents.py** - *(65 строк)* 🔗 Структура: [Def: get_agents, Def: create_agent, Def: update_agent, Def: delete_agent] 🔗 Зависимости: [json, fastapi, database, schemas, auth] `def get_agents(current_user | def create_agent(data | def update_agent(agent_id`
- **workspace/user_1/dev_agent/backend/core/routers/auth.py** - *(64 строк)* 🔗 Структура: [Def: register_user, Def: login_for_access_token, Def: read_users_me] 🔗 Зависимости: [fastapi, security, database, db_init, auth, schemas] `def register_user(user | def login_for_access_token(form_data`
- **workspace/user_1/dev_agent/backend/core/routers/keys.py** - *(172 строк)* 🔗 Структура: [Def: get_api_keys, Def: add_api_key, Def: delete_api_key, Def: get_keys_status, Def: get_or_balance_sync] 🔗 Зависимости: [urllib.request, json, asyncio, fastapi, database, schemas] `def get_api_keys(current_user | def add_api_key(data | def delete_api_key(key_id`
- **workspace/user_1/dev_agent/backend/core/routers/projects.py** - *(79 строк)* 🔗 Структура: [Def: get_projects, Def: create_project, Def: update_project, Def: reset_project_webhook, Def: delete_project] 🔗 Зависимости: [json, uuid, fastapi, database, schemas, auth] `def get_projects(current_user | def create_project(data | def update_project(project_id`
- **workspace/user_1/dev_agent/backend/core/routers/settings.py** - *(36 строк)* 🔗 Структура: [Def: get_settings, Def: update_settings] 🔗 Зависимости: [json, fastapi, database, schemas, auth, config] `def get_settings(current_user | def update_settings(data`
- **workspace/user_1/dev_agent/backend/core/routers/tasks.py** - *(312 строк)* 🔗 Структура: [Class: TaskContinue(), Def: get_tasks, Def: get_task_logs, Def: export_task_context, Def: export_task_debug] 🔗 Зависимости: [json, os, zipfile, io, re, fastapi] `class TaskContinue(BaseModel) | def get_tasks(current_user`
- **workspace/user_1/dev_agent/backend/core/routers/tools.py** - *(225 строк)* 🔗 Структура: [Class: FileRenameRequest(), Def: _get_safe_user_path, Def: get_tools, Def: update_tool, Def: local_read_file] 🔗 Зависимости: [os, json, shutil, re, fastapi, responses] `class FileRenameRequest(BaseModel) | def _get_safe_user_path(path | def get_tools(current_user`
- **workspace/user_1/dev_agent/backend/core/routers/ws.py** - *(38 строк)* 🔗 Зависимости: [fastapi, jose, config, state] `async def websocket_endpoint(websocket`
- **workspace/user_1/dev_agent/backend/core/schemas/agents.py** - *(16 строк)* 🔗 Структура: [Class: AgentCreateUpdate()] 🔗 Зависимости: [pydantic, typing] `class AgentCreateUpdate(BaseModel)`
- **workspace/user_1/dev_agent/backend/core/schemas/notes.py** - *(21 строк)* 🔗 Структура: [Class: NoteCategoryCreateUpdate(), Class: NoteCreateUpdate(), Class: NoteScheduleUpdate()] 🔗 Зависимости: [pydantic, typing] `class NoteCategoryCreateUpdate(BaseModel) | class NoteCreateUpdate(BaseModel) | class NoteScheduleUpdate(BaseModel)`
- **workspace/user_1/dev_agent/backend/core/schemas/tasks.py** - *(40 строк)* 🔗 Структура: [Class: ProjectCreateUpdate(), Class: TaskCreate(), Class: TaskToolConfirm(), Class: TaskToolResponse(), Class: ToolConfirm()] 🔗 Зависимости: [pydantic, typing] `class ProjectCreateUpdate(BaseModel) | class TaskCreate(BaseModel) | class TaskToolConfirm(BaseModel)`
- **workspace/user_1/dev_agent/backend/core/schemas/users.py** - *(30 строк)* 🔗 Структура: [Class: UserCreate(), Class: UserLogin(), Class: Token(), Class: UserData(), Class: SettingsUpdate()] 🔗 Зависимости: [pydantic, typing] `class UserCreate(BaseModel) | class UserLogin(BaseModel) | class Token(BaseModel)`
- **workspace/user_1/dev_agent/backend/core/schemas/__init__.py** - *(5 строк)* 🔗 Зависимости: [users, agents, tasks, notes] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/tasks/retriever.py** - *(70 строк)* 🔗 Зависимости: [json, database, llm] `async def get_relevant_tools(task_description`
- **workspace/user_1/dev_agent/backend/core/tasks/runner.py** - *(116 строк)* 🔗 Зависимости: [json, os, traceback, database, state, runner_db] `async def run_task(task_id`
- **workspace/user_1/dev_agent/backend/core/tasks/runner_context.py** - *(113 строк)* 🔗 Структура: [Def: setup_task_workspace, Def: build_system_prompt, Def: build_initial_messages, Def: get_active_manager_tools] 🔗 Зависимости: [os, json, re, datetime, database] `def setup_task_workspace(user_id | def build_system_prompt(agent_name`
- **workspace/user_1/dev_agent/backend/core/tasks/runner_db.py** - *(23 строк)* 🔗 Структура: [Def: log_task_action, Def: update_task_status, Def: is_task_cancelled] 🔗 Зависимости: [database] `def log_task_action(task_id | def update_task_status(task_id | def is_task_cancelled(task_id`
- **workspace/user_1/dev_agent/backend/core/tasks/runner_loop.py** - *(253 строк)* 🔗 Зависимости: [json, asyncio, time, os, traceback, datetime] `async def run_task_loop(`
- **workspace/user_1/dev_agent/backend/core/tasks/tool_handlers.py** - *(208 строк)* 🔗 Зависимости: [json, asyncio, os, shutil, database, state] `async def handle_tool_call(f_name`
- **workspace/user_1/dev_agent/backend/core/tasks/tools_impl/fs_code.py** - *(282 строк)* 🔗 Структура: [Def: _strip_zwsp] 🔗 Зависимости: [os, shutil, datetime, time, re, difflib] `def _strip_zwsp(text | async def execute_fs_code_tool(f_name`
- **workspace/user_1/dev_agent/backend/core/tasks/tools_impl/system.py** - *(175 строк)* 🔗 Структура: [Def: _strip_zwsp] 🔗 Зависимости: [os, json, time, re, urllib.parse, urllib.request] `def _strip_zwsp(text | async def execute_system_tool(f_name`
- **workspace/user_1/dev_agent/backend/core/tasks/tools_impl/utils.py** - *(110 строк)* 🔗 Структура: [Def: _hide_host_path, Def: _resolve_path, Def: _call_tool_node_sync] 🔗 Зависимости: [os, json, urllib.request, urllib.error, asyncio, re] `def _hide_host_path(text | def _resolve_path(path`
- **workspace/user_1/dev_agent/backend/core/tasks/tools_impl/_inspect_tmp.py** - *(14 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/core/tools/registry.py** - *(71 строк)* 🔗 Структура: [Def: sync_user_tools, Def: sync_tools_to_db] 🔗 Зависимости: [json, os, database] `def sync_user_tools(user_id`
- **workspace/user_1/dev_agent/backend/core/tools/tools.json** - *(494 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/tool_node/config.py** - *(11 строк)* 🔗 Зависимости: [os] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/tool_node/Dockerfile** - *(26 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/tool_node/main.py** - *(16 строк)* 🔗 Зависимости: [fastapi, uvicorn, fs, terminal, service] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/tool_node/schemas.py** - *(30 строк)* 🔗 Структура: [Class: FileWritePayload(), Class: FileReadPayload(), Class: CommandPayload(), Class: ServiceStartPayload(), Class: ServiceActionPayload()] 🔗 Зависимости: [pydantic] `class FileWritePayload(BaseModel) | class FileReadPayload(BaseModel) | class CommandPayload(BaseModel)`
- **workspace/user_1/dev_agent/backend/tool_node/state.py** - *(3 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/backend/tool_node/utils.py** - *(73 строк)* 🔗 Структура: [Def: get_safe_path, Def: build_sandbox_cmd] 🔗 Зависимости: [os, shutil, re, fastapi, config] `def get_safe_path(relative_path | def build_sandbox_cmd(command`
- **workspace/user_1/dev_agent/backend/tool_node/routers/fs.py** - *(43 строк)* 🔗 Зависимости: [os, fastapi, schemas, utils] `async def write_file(payload | async def read_file(payload`
- **workspace/user_1/dev_agent/backend/tool_node/routers/service.py** - *(82 строк)* 🔗 Зависимости: [os, uuid, subprocess, fastapi, schemas, utils] `async def start_service(payload | async def stop_service(payload | async def status_service(payload`
- **workspace/user_1/dev_agent/backend/tool_node/routers/terminal.py** - *(79 строк)* 🔗 Зависимости: [os, subprocess, fastapi, schemas, utils, config] `async def run_command(payload | def decode_output(b`
- **workspace/user_1/dev_agent/frontend/Dockerfile** - *(16 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/index.html** - *(13 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/nginx.conf** - *(49 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/README.md** - *(5 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/vite.config.js** - *(20 строк)* 🔗 Зависимости: [vite, plugin-vue] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/App.vue** - *(44 строк)* 🔗 Зависимости: [appStore, MainNav, Topbar, IdeModal] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/main.js** - *(42 строк)* 🔗 Зависимости: [App, SettingsView, StatisticsView, AggregatedStatsView, AgentsView, ToolsView] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/assets/main.css** - *(179 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/ide/IdeModal.vue** - *(325 строк)* 🔗 Зависимости: [appStore, api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/layout/MainNav.vue** - *(26 строк)* 🔗 Зависимости: [appStore] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/layout/Topbar.vue** - *(32 строк)* 🔗 Зависимости: [appStore] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/AskUserApproval.vue** - *(53 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/CodeApproval.vue** - *(76 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/DefaultApproval.vue** - *(27 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/ImageApproval.vue** - *(26 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/ImageGalleryResult.vue** - *(92 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/plugins/SearchImagesApproval.vue** - *(45 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/tasks/TaskCreateModal.vue** - *(89 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/tasks/TaskLogsArea.vue** - *(448 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/components/tasks/TasksSidebar.vue** - *(85 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/services/api.js** - *(159 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/stores/appStore.js** - *(78 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/AgentsView.vue** - *(435 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/AggregatedStatsView.vue** - *(125 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/AuthView.vue** - *(168 строк)* 🔗 Зависимости: [api, appStore] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/ProjectsView.vue** - *(245 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/SettingsView.vue** - *(273 строк)* `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/StatisticsView.vue** - *(106 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/TasksView.vue** - *(217 строк)* 🔗 Зависимости: [api, appStore, TasksSidebar, TaskLogsArea, TaskCreateModal] `[Конфиг / Без сигнатур]`
- **workspace/user_1/dev_agent/frontend/src/views/ToolsView.vue** - *(253 строк)* 🔗 Зависимости: [api] `[Конфиг / Без сигнатур]`
- **workspace/user_1/test/приветствие.txt** - *(1 строк)* `[Конфиг / Без сигнатур]`


# Карта API-эндпоинтов

- `PUT /{agent_id}` *(в backend/core/routers/agents.py)*
- `DELETE /{agent_id}` *(в backend/core/routers/agents.py)*
- `POST /register` *(в backend/core/routers/auth.py)*
- `POST /login` *(в backend/core/routers/auth.py)*
- `GET /me` *(в backend/core/routers/auth.py)*
- `GET /keys` *(в backend/core/routers/keys.py)*
- `POST /keys` *(в backend/core/routers/keys.py)*
- `DELETE /keys/{key_id}` *(в backend/core/routers/keys.py)*
- `GET /keys/status` *(в backend/core/routers/keys.py)*
- `GET /keys/balances` *(в backend/core/routers/keys.py)*
- `GET /statistics` *(в backend/core/routers/keys.py)*
- `GET /statistics/aggregated` *(в backend/core/routers/keys.py)*
- `PUT /{project_id}` *(в backend/core/routers/projects.py)*
- `POST /{project_id}/reset_webhook` *(в backend/core/routers/projects.py)*
- `DELETE /{project_id}` *(в backend/core/routers/projects.py)*
- `POST /{task_id}/continue` *(в backend/core/routers/tasks.py)*
- `GET /{task_id}/logs` *(в backend/core/routers/tasks.py)*
- `GET /{task_id}/context_export` *(в backend/core/routers/tasks.py)*
- `GET /{task_id}/debug_export` *(в backend/core/routers/tasks.py)*
- `POST /{task_id}/cancel` *(в backend/core/routers/tasks.py)*
- `POST /{task_id}/approve_tool` *(в backend/core/routers/tasks.py)*
- `POST /{task_id}/submit_tool_response` *(в backend/core/routers/tasks.py)*
- `PUT /{tool_id}` *(в backend/core/routers/tools.py)*
- `GET /fs/read` *(в backend/core/routers/tools.py)*
- `POST /fs/write` *(в backend/core/routers/tools.py)*
- `POST /fs/upload` *(в backend/core/routers/tools.py)*
- `GET /fs/list` *(в backend/core/routers/tools.py)*
- `DELETE /fs/delete` *(в backend/core/routers/tools.py)*
- `POST /fs/rename` *(в backend/core/routers/tools.py)*
- `POST /fs/mkdir` *(в backend/core/routers/tools.py)*
- `GET /fs/download` *(в backend/core/routers/tools.py)*
- `POST /write` *(в backend/tool_node/routers/fs.py)*
- `POST /read` *(в backend/tool_node/routers/fs.py)*
- `POST /start` *(в backend/tool_node/routers/service.py)*
- `POST /stop` *(в backend/tool_node/routers/service.py)*
- `POST /status` *(в backend/tool_node/routers/service.py)*
- `POST /logs` *(в backend/tool_node/routers/service.py)*
- `POST /run` *(в backend/tool_node/routers/terminal.py)*
- `PUT /{agent_id}` *(в workspace/user_1/dev_agent/backend/core/routers/agents.py)*
- `DELETE /{agent_id}` *(в workspace/user_1/dev_agent/backend/core/routers/agents.py)*
- `POST /register` *(в workspace/user_1/dev_agent/backend/core/routers/auth.py)*
- `POST /login` *(в workspace/user_1/dev_agent/backend/core/routers/auth.py)*
- `GET /me` *(в workspace/user_1/dev_agent/backend/core/routers/auth.py)*
- `GET /keys` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `POST /keys` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `DELETE /keys/{key_id}` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `GET /keys/status` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `GET /keys/balances` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `GET /statistics` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `GET /statistics/aggregated` *(в workspace/user_1/dev_agent/backend/core/routers/keys.py)*
- `PUT /{project_id}` *(в workspace/user_1/dev_agent/backend/core/routers/projects.py)*
- `POST /{project_id}/reset_webhook` *(в workspace/user_1/dev_agent/backend/core/routers/projects.py)*
- `DELETE /{project_id}` *(в workspace/user_1/dev_agent/backend/core/routers/projects.py)*
- `POST /{task_id}/continue` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `GET /{task_id}/logs` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `GET /{task_id}/context_export` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `GET /{task_id}/debug_export` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `POST /{task_id}/cancel` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `POST /{task_id}/approve_tool` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `POST /{task_id}/submit_tool_response` *(в workspace/user_1/dev_agent/backend/core/routers/tasks.py)*
- `PUT /{tool_id}` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `GET /fs/read` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `POST /fs/write` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `POST /fs/upload` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `GET /fs/list` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `DELETE /fs/delete` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `POST /fs/rename` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `POST /fs/mkdir` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `GET /fs/download` *(в workspace/user_1/dev_agent/backend/core/routers/tools.py)*
- `POST /write` *(в workspace/user_1/dev_agent/backend/tool_node/routers/fs.py)*
- `POST /read` *(в workspace/user_1/dev_agent/backend/tool_node/routers/fs.py)*
- `POST /start` *(в workspace/user_1/dev_agent/backend/tool_node/routers/service.py)*
- `POST /stop` *(в workspace/user_1/dev_agent/backend/tool_node/routers/service.py)*
- `POST /status` *(в workspace/user_1/dev_agent/backend/tool_node/routers/service.py)*
- `POST /logs` *(в workspace/user_1/dev_agent/backend/tool_node/routers/service.py)*
- `POST /run` *(в workspace/user_1/dev_agent/backend/tool_node/routers/terminal.py)*
