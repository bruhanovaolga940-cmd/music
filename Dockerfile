# Этап 1: сборка React
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Этап 2: бэкенд на Python + FFmpeg + Deno
FROM python:3.11-slim
WORKDIR /app

# Устанавливаем ffmpeg и утилиты для скачивания Deno
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Deno для обхода защиты потоков YouTube в yt-dlp
RUN curl -fsSL https://deno.land | DENO_INSTALL=/usr/local sh

# Устанавливаем зависимости Python из fastapi/requirements.txt
COPY fastapi/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -U --pre "yt-dlp[default,curl-cffi]" yt-dlp-ejs

# Копируем содержимое папки fastapi (внутри появится папка app)
COPY fastapi/ ./

# Копируем собранный фронтенд в /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Запускаем FastAPI на порту Railway
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
