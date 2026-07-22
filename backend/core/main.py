# backend/core/main.py
import asyncio
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from backend.core.database import close_db_pool
from backend.core.db_init import init_db, reset_running_tasks
from backend.core.state import state
from backend.core.agents.background import start_background_worker
from backend.core.tools.registry import sync_tools_to_db

from backend.core.routers.auth import router as auth_router
from backend.core.routers.settings import router as settings_router
from backend.core.routers.agents import router as agents_router
from backend.core.routers.keys import router as keys_router
from backend.core.routers.tools import router as tools_router
from backend.core.routers.tasks import router as tasks_router
from backend.core.routers.projects import router as projects_router
from backend.core.routers.ws import router as ws_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    sync_tools_to_db()
    reset_running_tasks()
    asyncio.create_task(start_background_worker(state.broadcast_ws))

@app.on_event("shutdown")
async def shutdown_event():
    close_db_pool()

app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(agents_router)
app.include_router(keys_router)
app.include_router(tools_router)
app.include_router(tasks_router)
app.include_router(projects_router)
app.include_router(ws_router)

if __name__ == "__main__":
    uvicorn.run("backend.core.main:app", host="0.0.0.0", port=8180, reload=True, access_log=False)
