from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import rag_service

router = APIRouter()


@router.post("/", response_model=ChatResponse, summary="發送訊息給 AI 角色")
async def chat(request: ChatRequest):
    """
    接收使用者訊息，透過 RAG 引擎從知識庫中取得相關背景資料，
    再呼叫 Ollama LLM 生成角色回應，最後回傳結構化 JSON。
    """
    try:
        result = rag_service.query(message=request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
