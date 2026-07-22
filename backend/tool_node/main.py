# backend/tool_node/main.py
from fastapi import FastAPI
import uvicorn

from backend.tool_node.routers.fs import router as fs_router
from backend.tool_node.routers.terminal import router as terminal_router
from backend.tool_node.routers.service import router as service_router

app = FastAPI()

app.include_router(fs_router)
app.include_router(terminal_router)
app.include_router(service_router)

if __name__ == "__main__":
    uvicorn.run("backend.tool_node.main:app", host="0.0.0.0", port=8181, reload=True)
