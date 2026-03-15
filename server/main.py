import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import warnings

# 隱藏 langchain 產生的 Pydantic V1/V2 兼容性噪音警告 (不影響運行)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.v1.fields")
warnings.filterwarnings("ignore", category=UserWarning, message=".*Pydantic V1 functionality.*")

from app.api.v1 import api_router

app = FastAPI(
    title="AIRPG Backend",
    description="AI Role-playing Game Backend API. Provides RAG-enhanced character dialogue functionality.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 設定 CORS，允許所有來源 (開發階段方便 Godot 連線，生產環境需限制)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 v1 路由，所有端點皆以 /api/v1 為前綴
app.include_router(api_router, prefix="/api/v1")

# Godot 匯出的 Web 遊戲：若 GAME_STATIC_PATH 或專案根目錄 dist/ 存在，則掛載於 /game
_game_path = Path(os.getenv("GAME_STATIC_PATH", Path(__file__).resolve().parent.parent / "dist"))
if _game_path.exists():
    app.mount("/game", StaticFiles(directory=str(_game_path), html=True), name="game")


@app.get("/", tags=["Root"])
async def root():
    """Root - 確認伺服器運行狀態"""
    return {"status": "ok", "message": "AIRPG Backend v0.2.0 is running"}


@app.get("/health", tags=["Root"])
async def health_check():
    """Health Check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
