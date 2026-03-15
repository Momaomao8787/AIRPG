# AIRPG 錯誤碼與訊息說明文件

本文件列出 AIRPG 專案中可能遇到的錯誤及其代表的意義，幫助開發者與使用者進行快速排錯。

---

## 1. Launcher Dashboard 錯誤 (8080 埠)

Launcher 透過 JSON 回傳操作狀態，常見的錯誤訊息如下：

### 1.1 服務管理錯誤

| 錯誤訊息 (`message`) | 原因 | 建議操作 |
| :--- | :--- | :--- |
| `Backend is already running.` | 後端 FastAPI 進程已經在背景執行中。 | 無需操作。若需重啟，請先點擊「停止伺服器」。 |
| `Backend service is not running.` | 嘗試停止、清空日誌或進行其他操作時，後端服務並未運行。 | 先點擊「啟動伺服器」。 |
| `Cannot find run_server.bat` | 找不到啟動後端的批次檔。 | 檢查 `server/` 目錄下是否存在 `run_server.bat`。 |
| `Cannot find ingest.py` | 找不到知識庫處理腳本。 | 檢查 `server/app/rag/ingest.py` 是否存在。 |

---

## 2. 後端 API 錯誤 (8000 埠)

後端基於 FastAPI，遵循標準 HTTP 狀態碼。

### 2.1 HTTP 狀態碼說明

| 狀態碼 | 名稱 | 專案中的具體意義 |
| :--- | :--- | :--- |
| `200` | OK | 請求成功，AI 已成功產生回應。 |
| `422` | Unprocessable Entity | **請求格式錯誤**。通常是因為前端發送的 JSON 不符合 `ChatRequest` 的定義（例如缺少 `message` 欄位）。 |
| `404` | Not Found | **路徑錯誤**。請求了不存在的 API 端點。 |
| `500` | Internal Server Error | **後端內部錯誤**。常見原因包括 Ollama 服務未啟動、LLM 連線逾時或 RAG 檢索邏輯出錯。 |

### 2.2 詳細錯誤對應 (HTTP 500 Detail)

當發生 `500` 錯誤時，回應的 `detail` 欄位會包含具體報錯文字：

*   **`Connection refused`**: Ollama 服務未開啟。請確保執行了 `ollama serve`。
*   **`Collection not found`**: 向量資料庫（ChromaDB）尚未建立。請先在 Launcher 點擊「更新知識庫」。
*   **`Model not found`**: 指定的 LLM 或 Embedding 模型尚未下載。請執行 `ollama pull [model_name]`。
*   **`AttributeError` / `TypeError`**: 程式碼邏輯或輸入型別錯誤（已於 v0.2.1 進行了大規模修正與型別保護）。

---

## 3. 日誌系統 (Logs)

若在 Dashboard 的日誌視窗中看到以下前綴：

*   **`[SYSTEM]`**: 來自 Launcher Server 的管理訊息（例如啟動/停止通知）。
*   **`[ingest]`**: 來自 `ingest.py` 的知識庫更新進度。
*   **`[ERROR]`**: 來自 FastAPI 或終端輸出的標準錯誤訊息。

---

*最後更新時間：2026-03-14*
