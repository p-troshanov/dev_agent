# backend/core/agents/bg_tasks/state.py
import asyncio

# Централизованное хранилище стейта фоновых воркеров
agent_queue = asyncio.Queue()
_broadcast_callback = None

def set_broadcast_callback(cb):
    global _broadcast_callback
    _broadcast_callback = cb

def get_broadcast_callback():
    return _broadcast_callback
