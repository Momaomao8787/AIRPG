from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """使用者發送給 API 的請求格式"""
    user_id: str = Field(..., description="使用者的唯一識別碼")
    message: str = Field(..., description="使用者輸入的訊息")
    character_id: str = Field(default="default", description="角色識別碼")

class RagContext(BaseModel):
    """RAG 從知識庫中取回的參考片段"""
    content: str
    source: Optional[str] = None

class ChatResponse(BaseModel):
    """API 回傳給前端的回應格式"""
    response: str = Field(..., description="AI 角色的回應文字")
    emotion: str = Field(default="neutral", description="AI 角色的情緒狀態")
    animation_trigger: Optional[str] = Field(default=None, description="觸發的動畫指令")
    rag_context: list[str] = Field(default_factory=list, description="RAG 參考的知識片段")

class ErrorResponse(BaseModel):
    """錯誤回應格式"""
    error: str
