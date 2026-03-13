# AI Immersive Role-Playing Agent System (AIRPA)
> **專案規格與架構設計**

## 1. 專案概述
本專案旨在建構一個高互動性的 AI 角色扮演對話系統。區別於一般的 Chatbot，本系統結合 **RAG** 技術，使 AI 角色能夠嚴格遵循特定的「世界觀設定集 (World Bible)」與使用者互動，並透過 **Godot Engine** 提供沉浸式的 Web 前端體驗。

### 核心目標
*   **前後端分離架構**: 前端負責互動展演，後端負責 AI 邏輯與狀態管理。
*   **上下文感知**: 利用 RAG 技術解決 LLM 的幻覺問題，確保角色對話符合設定。
*   **沉浸式體驗**: 透過 Godot Web Export 提供比傳統網頁更豐富的視覺與動態回饋。

---

## 2. 系統架構
本系統採用 **Client-Server** 架構。

### 架構圖
```mermaid
graph TD
    User -->|操作| Client[前端: Godot Web App]
    Client -->|HTTP POST (JSON)| API[後端: FastAPI Server]
    
    subgraph "後端服務 (Python)"
        API -->|1. 查詢上下文| RAG[RAG Engine]
        API -->|4. 生成回應| LLM[LLM Service (Ollama/OpenAI)]
        
        RAG -->|2. 向量檢索| VectorDB[(ChromaDB)]
        RAG -->|3. 注入 Prompt| LLM
    end
    
    VectorDB <-->|預處理: Embedding| WorldData[世界觀設定檔]
```

### 技術堆疊
| 模組 | 技術選型 | 用途說明 |
| :--- | :--- | :--- |
| **前端** | Godot Engine 4.4 | 負責 UI 呈現、動畫效果、HTTP 請求處理。 |
| **後端** | Python 3.10+ | 核心邏輯基礎語言。 |
| **API 框架** | FastAPI | 提供高效能的 RESTful API 端點。 |
| **LLM 編排** | LangChain / LlamaIndex | 負責 Prompt Template 管理與 RAG 流程串接。 |
| **向量資料庫** | ChromaDB | 本地端輕量級向量資料庫，儲存知識嵌入。 |
| **模型推理** | Ollama (本地) / OpenAI API | 提供 LLM 推論與 Embedding 能力。<br>建議模型：<br>對話：`llama3`, `mistral`<br>嵌入：`nomic-embed-text` |

---

## 3. 功能需求

### 3.1 前端功能
1.  **對話介面**: 包含對話歷史顯示區、使用者輸入框 (LineEdit)、發送按鈕。
2.  **狀態顯示**: 顯示 AI 當前狀態 (思考中、輸入中、閒置)。
3.  **網路通訊**: 使用 `HTTPRequest` 節點發送資料至後端 API。
4.  **錯誤處理**: 當 API 連線失敗或逾時時，顯示重試提示。

### 3.2 後端功能
1.  **API 端點**: 提供 `/chat` 與 `/health` 接口。
2.  **RAG 流程**:
    *   **知識導入**: 啟動時自動讀取世界觀設定，進行文字切塊並存入向量庫。
    *   **檢索**: 根據使用者輸入，檢索最相關的世界觀片段。
3.  **記憶管理**: 暫存對話歷史，使 AI 能夠維持對話上下文。
4.  **提示工程**: 動態組合系統指令、背景知識與使用者輸入。

---

## 4. API 規格
後端伺服器預設運行於 `http://localhost:8000`。

### 4.1 對話請求
*   **端點**: `POST /api/v1/chat`
*   **Content-Type**: `application/json`

#### 請求主體 (Request Body)
```json
{
  "user_id": "player_001",
  "message": "請問這座森林的歷史是什麼？",
  "character_id": "elf_ranger"
}
```

#### 回應主體 (Success 200)
```json
{
  "response": "這座森林名為『蒼翠之森』，在三百年前的大戰中...",
  "mood": "calm",
  "rag_context": ["蒼翠之森歷史片段...", "精靈族起源..."]
}
```

#### 回應主體 (Error 500)
```json
{
  "error": "LLM Service Unavailable"
}
```

---

## 5. 資料流設計

### 知識庫處理流程
1.  **加載**: 讀取世界觀文件。
2.  **切分**: 使用 `RecursiveCharacterTextSplitter` 將文本切分為 500-1000 tokens 的區塊。
3.  **嵌入**: 將文字轉為向量。
4.  **存儲**: 存入 ChromaDB 持久化存儲。

### 推論流程
當收到使用者訊息時：
1.  **搜索**: 在 ChromaDB 搜尋相似度最高的相關片段。
2.  **建構提示**:
    ```text
    系統指令: 你是 [角色名稱]，請依據以下世界觀回答問題，並保持角色語氣。

    參考資料:
    {Context}

    使用者問題:
    {UserQuery}
    ```
3.  **生成**: 送入 LLM 生成回應。
4.  **回傳**: 回傳文字與表情狀態給前端。

---

## 6. 開發路線圖
### 第一階段：基礎建設
- [x] **Python 環境配置**: 建立虛擬環境 (venv) 並管理套件。
- [/] **FastAPI 核心**: 架設伺服器並實作基礎 Health Check 接口。


### 第二階段：核心邏輯實作
- [x] **RAG 引擎整合**: 已導入 LangChain 與 ChromaDB 並完成 Ingestion 修復。
- [x] **知識庫處理**: 實作 `ingest.py` 支援 `.md` 文檔，完成向量化腳本開發。
- [ ] **對話檢索優化**: 驗證 API 能精確檢索並根據世界觀回傳內容。
- [ ] **長期記憶**: 支援對話歷史管理，維持連貫脈絡。

### 第三階段：前端開發
- [ ] **Godot 基礎通訊**: 建立基本 UI，完成與後端 API 的初步對接。
- [ ] **感官優化**: 實作 Godot 對話框與打字機動效，優化Latency。

### 第四階段：部署
- [ ] **容器化部署**: 撰寫 Dockerfile 與 docker-compose 配置文件。

---

## 7. 安裝與執行

### 前置需求
*   **Python**: 3.10+
*   **Godot**: 4.2+
*   **Ollama**: 已安裝並下載必要模型：
    *   推論模型：`llama3` (或自選)
    *   嵌入模型：`nomic-embed-text` (RAG 核心需求)

### 啟動後端
```bash
# 1. 建立並啟動虛擬環境
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. 安裝必要套件
pip install -r requirements.txt

# 3. 執行開發伺服器
uvicorn main:app --reload
```

### 啟動前端
1.  使用 **Godot Engine** 開啟專案資料夾。
2.  按下 `F5` 鍵直接執行專案，或匯出為 **Web (HTML5)** 格式。
