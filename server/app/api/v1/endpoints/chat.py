import logging
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse, summary="Send message to AI character")
async def chat(request: ChatRequest):
    """
    Receive user message, retrieve relevant background from knowledge base via RAG,
    call LLM to generate character response, and return structured JSON.
    Currently only request.message is used; user_id and character_id are reserved for future multi-user/multi-character support.
    """
    msg = request.message
    if not (msg and msg.strip()):
        raise HTTPException(status_code=422, detail="message cannot be empty.")
    if len(msg) > 4000:
        raise HTTPException(status_code=422, detail="message too long.")
    try:
        result = rag_service.query(message=msg.strip())
        return ChatResponse(**result)
    except Exception as e:
        logger.exception("Chat endpoint error: %s", e)
        msg = str(e).lower()
        if "connection" in msg or "timeout" in msg or "unavailable" in msg or "refused" in msg:
            raise HTTPException(status_code=503, detail="LLM or knowledge base service temporarily unavailable.")
        raise HTTPException(status_code=500, detail="Internal server error.")
