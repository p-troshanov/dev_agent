# backend/tool_node/config.py
import os

_default_workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workspace"))
_env_workspace = os.getenv("WORKSPACE_DIR")

# Если мы на Windows, а в .env путь от Docker (/workspace), принудительно используем локальную папку
if _env_workspace and os.name == 'nt' and _env_workspace.startswith('/'):
    BASE_WORKSPACE = _default_workspace
else:
    BASE_WORKSPACE = _env_workspace or _default_workspace
