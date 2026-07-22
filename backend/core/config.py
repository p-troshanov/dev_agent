# backend/core/config.py
import os
import urllib.parse
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

# Настройки базы данных
_user = os.getenv("POSTGRES_USER", "postgres")
_password = os.getenv("POSTGRES_PASSWORD", "postgres")
_host = os.getenv("POSTGRES_HOST", "db") # Имя сервиса БД в docker-compose
_port = os.getenv("POSTGRES_PORT", "5432")
_db = os.getenv("POSTGRES_DB", "rita")

# Безопасное кодирование пароля (чтобы символы типа %, @, # не ломали URL)
safe_password = urllib.parse.quote_plus(_password)
default_url = f"postgresql://{_user}:{safe_password}@{_host}:{_port}/{_db}"

POSTGRES_URL = os.getenv("POSTGRES_URL", default_url)

# Настройки авторизации
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Внутренняя маршрутизация
TOOL_NODE_URL = os.getenv("TOOL_NODE_URL", "http://tool_node:8181")

DEFAULT_SETTINGS = {
    "user_name": "Вы",
    "weather_city": "Москва",
    "avatar": None,
    "timezone": "Europe/Moscow"
}
