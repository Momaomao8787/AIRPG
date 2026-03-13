# AIRPG 後端開發教學 - RAG 對話 API 實作指南

> 本文件說明如何在 AIRPG 專案中建構一個具備 RAG（Retrieval-Augmented Generation）能力的對話 API。讀完本指南後，你將理解從知識庫建置到 API 端點呼叫的完整流程。

---

## 目錄

1. [系統架構概覽](#1-系統架構概覽)
2. [知識庫建置 (Ingestion)](#2-知識庫建置-ingestion)
3. [RAG Chain 設計](#3-rag-chain-設計)
4. [API 端點實作](#4-api-端點實作)
5. [啟動與測試](#5-啟動與測試)
6. [常見問題](#6-常見問題)

---

## 1. 系統架構概覽

本後端採用「**分層模組化**」設計，職責清晰分離：

```
server/
├── main.py                   # FastAPI 應用程式進入點，掛載路由
├── app/
│   ├── core/
│   │   └── config.py         # 集中管理路徑與模型設定
│   ├── schemas/
│   │   └── chat.py           # Pydantic 請求/回應模型 (資料驗證)
│   ├── services/
│   │   └── rag_service.py    # 核心 RAG 邏輯 (與 LLM / ChromaDB 互動)
│   └── api/
│       └── v1/
│           ├── __init__.py   # v1 路由總入口
│           └── endpoints/
│               └── chat.py   # /api/v1/chat/ 端點定義
└── app/
    └── rag/
        └── ingest.py         # 知識庫預處理腳本 (一次性執行)
```

**請求流程**：
```
使用者輸入 → POST /api/v1/chat/
  → Pydantic 驗證請求格式
    → rag_service.query()
      → ChromaDB 向量檢索 (取得最相關的 K 個知識片段)
        → 注入 Prompt (世界觀背景 + 使用者問題)
          → Ollama LLM 生成 JSON 格式回應
            → 回傳 ChatResponse 給前端
```

---

## 2. 知識庫建置 (Ingestion)

在啟動 API 之前，必須先執行一次 `ingest.py` 將世界觀文件轉換為向量並存入 ChromaDB。

### 2.1 準備知識庫文件

將所有 `.md` 格式的世界觀文件放入 `server/data/` 目錄。

**範例文件結構 (`data/world.md`)**：
```markdown
# 蒼翠之森

蒼翠之森是一片位於大陸中央的古老森林，已有三千年歷史。

## 居民
精靈族在此定居已逾千年，守護著森林的魔法結界。

## 禁忌
外來者不得在夜間進入森林深處，違者將迷失於幻境之中。
```

### 2.2 執行 Ingestion 腳本

```bash
# 啟動虛擬環境後執行
python app/rag/ingest.py
```

**腳本做了什麼？**

| 步驟 | 說明 |
|:---|:---|
| 1. 加載 | 讀取 `data/` 目錄下所有 `.md` 文件 |
| 2. 切塊 | 使用 `RecursiveCharacterTextSplitter` 將文本切割為 500 字的區塊（重疊 50 字） |
| 3. 嵌入 | 使用 Ollama `nomic-embed-text` 模型將文字轉為向量 |
| 4. 存儲 | 將向量持久化存入 `chroma_db/` 目錄 |

> **注意**: 每次執行會清空舊的 ChromaDB。若需要增量更新，需要修改 `ingest.py` 的邏輯。

---

## 3. RAG Chain 設計

`services/rag_service.py` 是整個系統的核心。

### 3.1 系統提示詞 (System Prompt)

系統提示詞定義了 AI 角色的行為約束：

```python
SYSTEM_PROMPT = """你是一個沉浸式 AI 角色扮演助理。請嚴格依照以下「世界觀背景資料」來回答問題。
請以第一人稱扮演角色，切勿說出「我是 AI」等出戲的話語。

請務必以以下 JSON 格式回應：
{
  "response": "角色的對話台詞",
  "emotion": "當前情緒 (neutral/happy/sad/angry/mysterious/surprised 之一)",
  "animation_trigger": "動畫指令 (idle/talk/nod/shake_head 之一，或 null)"
}

【世界觀背景資料】
{context}
"""
```

> **關鍵設計**: 要求 LLM 輸出**結構化 JSON** 而非純文字，讓前端（Godot）可以同時控制角色的文字、表情與動畫。

### 3.2 LCEL Chain 串接

使用 LangChain Expression Language (LCEL) 串接各元件：

```python
rag_chain = (
    {
        "context": retriever | _format_docs,  # 1. 檢索 → 格式化
        "question": RunnablePassthrough(),     # 2. 使用者問題直接傳遞
    }
    | prompt   # 3. 注入 Prompt 模板
    | llm      # 4. LLM 生成
    | StrOutputParser()  # 5. 取出純文字
)
```

### 3.3 JSON 解析容錯

LLM 有時會在 JSON 外包裹 Markdown 的程式碼區塊（` ```json ` ），因此需要清理：

```python
cleaned = raw_output.strip().removeprefix("```json").removesuffix("```").strip()
try:
    parsed = json.loads(cleaned)
except json.JSONDecodeError:
    # 解析失敗時，直接將原始文字作為 response 回傳
    parsed = {"response": raw_output, "emotion": "neutral"}
```

---

## 4. API 端點實作

### 4.1 請求與回應格式

**請求 (`ChatRequest`)**：
```json
{
  "user_id": "player_001",
  "message": "請問這座森林有什麼禁忌？",
  "character_id": "elf_ranger"
}
```

**成功回應 (`ChatResponse`)**：
```json
{
  "response": "夜晚切勿踏入深林...那裡住著看不見的東西。",
  "emotion": "mysterious",
  "animation_trigger": "idle",
  "rag_context": [
    "外來者不得在夜間進入森林深處，違者將迷失於幻境之中。",
    "..."
  ]
}
```

### 4.2 路由架構

FastAPI 的路由採用**版本化設計**，方便未來維護：

```
main.py
  └── app.include_router(api_router, prefix="/api/v1")
       └── api/v1/__init__.py (api_router)
            └── chat.router (prefix="/chat")
                 └── POST /  → 最終路徑: POST /api/v1/chat/
```

---

## 5. 啟動與測試

### 5.1 前置條件

確認 Ollama 已啟動，且以下模型已下載：
```bash
ollama pull nomic-embed-text  # Embedding 模型
ollama pull llama3             # 對話模型
```

### 5.2 啟動後端

```bash
# 在 server/ 目錄下執行
.\\venv\\Scripts\\activate
python app/rag/ingest.py    # 首次執行需建置知識庫
uvicorn main:app --reload
```

### 5.3 測試端點

**測試 Health Check**：
```bash
# PowerShell
(Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing).Content
```

**測試 Chat 端點 (Python)**：
```python
import urllib.request, json

payload = {
    "user_id": "test_user",
    "message": "你好，請介紹一下這座森林。",
    "character_id": "elf"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/chat/",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as r:
    print(json.loads(r.read()))
```

**使用 API 文件 (推薦)**：
開瀏覽器訪問 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)，FastAPI 會自動產生互動式 Swagger UI。

---

## 6. 常見問題

| 問題 | 可能原因 | 解決方法 |
|:---|:---|:---|
| `Connection refused` | Ollama 服務未啟動 | 執行 `ollama serve` |
| `Collection not found` | ChromaDB 尚未初始化 | 執行 `python app/rag/ingest.py` |
| LLM 回傳非 JSON 格式 | 模型遵循指令能力較弱 | 更換模型或調整 Prompt |
| Import Error | 未啟動 venv | 執行 `.\\venv\\Scripts\\activate` |

---

*最後更新：2026-03-09*
