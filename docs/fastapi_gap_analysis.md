# FastAPI 核心功能缺失分析報告

根據 [README.md](file:///c:/Users/user/Documents/DevilCatGames/AIRPG/README.md) 的規劃與目前 [server/main.py](file:///c:/Users/user/Documents/DevilCatGames/AIRPG/server/main.py) 的實作進度，以下是 FastAPI 核心部分目前缺失的關鍵組件：

## 1. 核心端點缺失 (Core Endpoints)
*   **`POST /api/v1/chat`**: 這是整個系統最核心的 API，目前完全尚未實作。
*   **缺乏輸入驗證 (Pydantic Models)**: 尚未定義 `ChatRequest` (包含 `user_id`, `message`, `character_id`) 與 `ChatResponse` 的資料結構。

## 2. 業務邏輯整合缺失 (Logic Integration)
*   **RAG 檢索流程 (Retrieval Logic)**: 雖然已有 [ingest.py](file:///c:/Users/user/Documents/DevilCatGames/AIRPG/server/app/rag/ingest.py) 建立知識庫，但後端 API 尚未實作「接收問題 -> 向量檢索 -> 獲取 Context」的調用邏輯。
*   **LLM 服務串接 (LLM Service)**: 尚未建立與本地 Ollama 或 OpenAI API 的連線代碼，無法將檢索到的 Context 送入模型生成回應。
*   **提示詞管理 (Prompt Engineering)**: 尚未實作 `Prompt Template`，無法動態組裝系統指令、背景知識與使用者訊息。

## 3. 架構層面缺失 (Architectural Gaps)
*   **路由模組化 (Modular Routing)**: 目前所有代碼都在 [main.py](file:///c:/Users/user/Documents/DevilCatGames/AIRPG/server/main.py)。隨著功能增加，應將 API 分解為 `app/api/v1/endpoints/chat.py` 等模組。
*   **依賴注入 (Dependency Injection)**: 尚未實做資料庫連線池 (ChromaDB Client) 或 LLM 客戶端的單例管理（Singleton）。
*   **異常處理 (Global Exception Handler)**: 缺乏針對 LLM 逾時、資料庫連線失敗等情況的全局錯誤捕捉機制。

## 4. 記憶與狀態缺失 (Memory & State)
*   **對話歷史 (Dialogue History)**: 尚未實作 Session 控制，AI 無法記住前幾輪的對話內容（短期記憶）。

---

## 建議優先實作順序
1.  **定義 Data Models**: 使用 Pydantic 定義 API 請求與回應格式。
2.  **建立 RAG Query 邏輯**: 實作一個能從 ChromaDB 檢索相關片段的函數。
3.  **整合 LLM**: 實作調用 Ollama 的服務模組。
4.  **開啟 `/chat` 路由**: 串接以上組件，完成「端到端」的對話。
