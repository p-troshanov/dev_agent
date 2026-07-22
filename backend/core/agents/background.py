# backend/core/agents/background.py
import asyncio
from backend.core.agents.bg_tasks.state import agent_queue, set_broadcast_callback

async def start_background_worker(broadcast_cb):
    set_broadcast_callback(broadcast_cb)
    print("🚀 [BACKGROUND WORKER] Запущен...")
    while True:
        task = await agent_queue.get()
        try:
            pass # Резерв на будущее для обработки фоновых задач агентов 
        except Exception as e:
            print(f"❌ Ошибка [BACKGROUND WORKER]: {e}")
        finally:
            agent_queue.task_done()
            await asyncio.sleep(0.5)
