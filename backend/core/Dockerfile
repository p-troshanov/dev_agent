# backend/core/Dockerfile
FROM python:3.13-slim

WORKDIR /app


# Добавили ffmpeg в список установки
RUN apt-get update && apt-get install -y gcc curl libffi-dev portaudio19-dev python3-dev ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/core /app/backend/core

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8180

CMD ["uvicorn", "backend.core.main:app", "--host", "0.0.0.0", "--port", "8180"]
