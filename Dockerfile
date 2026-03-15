# AIRPG: single image for backend (FastAPI) and launcher (dashboard + ingest)
FROM python:3.11-slim

WORKDIR /app

# Copy server and launcher (client/ excluded via .dockerignore)
COPY server/ /app/server/
COPY launcher/ /app/launcher/

RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Godot Web 匯出目錄（執行期由 volume 掛載 dist → /app/static/game）
ENV GAME_STATIC_PATH=/app/static/game
RUN mkdir -p /app/static/game

EXPOSE 8000 8080

# Default: run backend (override in compose for launcher)
WORKDIR /app/server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
