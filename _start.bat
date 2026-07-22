:: _start.bat
@echo off
chcp 65001 > nul
echo Запуск микросервисов RITA с использованием виртуального окружения...

echo Убедитесь, что у вас работает локальный PostgreSQL на порту 5432.

:: Создаем виртуальное окружение в корне, если его нет
if not exist "venv" (
    echo Создаю виртуальное окружение venv...
    python -m venv venv
)

:: Активируем venv, обновляем установщики и ставим зависимости
echo Обновление pip и установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install watchfiles

:: Запуск tool_node (порт 8181)
start "Tool Node" cmd /k "call venv\Scripts\activate.bat && set PYTHONPATH=. && uvicorn backend.tool_node.main:app --host 0.0.0.0 --port 8181 --reload --reload-dir backend"

:: Запуск core (порт 8180)
start "Core" cmd /k "call venv\Scripts\activate.bat && set PYTHONPATH=. && set TOOL_NODE_URL=http://localhost:8181 && uvicorn backend.core.main:app --host 0.0.0.0 --port 8180 --reload --reload-dir backend"

:: Даем бэкенду 3 секунды на запуск перед стартом фронтенда
echo Ожидание запуска бэкенда...
timeout /t 3 /nobreak > nul

:: Запуск frontend
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo Все компоненты запущены в отдельных окнах терминала!
pause