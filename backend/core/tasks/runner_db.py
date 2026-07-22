# backend/core/tasks/runner_db.py
from backend.core.database import get_db

def log_task_action(task_id: int, role: str, content: str, agent_name: str, tool_call_id: str = None, pending_approval: int = 0):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''INSERT INTO task_logs (task_id, role, content, agent_name, tool_call_id, pending_approval) 
                         VALUES (%s, %s, %s, %s, %s, %s)''', (task_id, role, content, agent_name, tool_call_id, pending_approval))
        conn.commit()

def update_task_status(task_id: int, status: str):
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('UPDATE tasks SET status = %s WHERE id = %s', (status, task_id))
        conn.commit()

def is_task_cancelled(task_id: int) -> bool:
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT is_cancelled FROM tasks WHERE id = %s", (task_id,))
            row = c.fetchone()
            return row and row[0] == 1

