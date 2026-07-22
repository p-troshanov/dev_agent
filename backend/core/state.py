# backend/core/state.py
class AppState:
    def __init__(self):
        self.active_frontend_connections = {}
        self.active_generation_id = {}
        self.pending_tool_calls = {}
        self.pending_task_tools = {}

    def add_connection(self, user_id: int, websocket):
        if user_id not in self.active_frontend_connections:
            self.active_frontend_connections[user_id] = []
        self.active_frontend_connections[user_id].append(websocket)
        if user_id not in self.active_generation_id:
            self.active_generation_id[user_id] = 0

    def remove_connection(self, user_id: int, websocket):
        if user_id in self.active_frontend_connections:
            if websocket in self.active_frontend_connections[user_id]:
                self.active_frontend_connections[user_id].remove(websocket)

    async def broadcast_ws(self, message: dict, user_id: int = None):
        if user_id is not None:
            conns = self.active_frontend_connections.get(user_id, [])
            for ws in list(conns):
                try:
                    await ws.send_json(message)
                except Exception:
                    pass
        else:
            for uid, conns in list(self.active_frontend_connections.items()):
                for ws in list(conns):
                    try:
                        await ws.send_json(message)
                    except Exception:
                        pass

state = AppState()
