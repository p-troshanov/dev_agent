# backend/tool_node/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Устанавливаем утилиты для песочницы агента (git, nodejs, npm, bubblewrap),
# а также системные зависимости для успешной сборки requirements.txt (gcc, portaudio19-dev, python3-dev)
RUN apt-get update && apt-get install -y \
    git curl nodejs npm bubblewrap \
    gcc libffi-dev portaudio19-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/tool_node /app/backend/tool_node

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Создаем папку-песочницу
RUN mkdir -p /workspace

EXPOSE 8181

CMD ["uvicorn", "backend.tool_node.main:app", "--host", "0.0.0.0", "--port", "8181"]
