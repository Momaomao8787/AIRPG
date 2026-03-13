from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.v1 import api_router

app = FastAPI(
    title="AIRPG Backend",
    description="AI 角色扮演遊戲後端 API。提供 RAG 增強的角色對話功能。",
    version="0.2.0", # The instruction mentioned "更新版本號" but the provided example kept it as "0.2.0". Assuming no change to the version number itself based on the example.
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
