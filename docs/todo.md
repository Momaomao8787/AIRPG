# Project Tasks

## 第一階段：基礎建設
- [x] Python 環境配置 (venv)
- [x] FastAPI 核心實做
    - [x] 基礎伺服器架構 (`main.py`)
    - [x] 健康檢查端點 (`/health`)
    - [x] `/chat` 對話端點 (`POST /api/v1/chat/`)
- [ ] Godot 基礎通訊 (Client 端為空)

## 第二階段：核心邏輯實做
- [x] RAG 引擎整合 (已更換為高效能 nomic-embed-text 模型)
- [x] 知識庫處理 (已支援 .md 並提供開發邏輯教學)
- [x] 對話 API 實作
    - [x] `core/config.py` - 集中設定管理
    - [x] `schemas/chat.py` - Pydantic 資料模型
    - [x] `services/rag_service.py` - RAG Chain (LCEL + JSON 輸出)
    - [x] `api/v1/endpoints/chat.py` - 端點定義
- [ ] 對話檢索優化 (實際對話測試)
- [ ] 長期記憶支援

## 第三階段：開發體驗與部署
- [x] **開發體驗優化**
    - [x] 一鍵啟動腳本 (`start_dev.bat`)
    - [x] Ollama 自動診斷與啟動服務
    - [x] 模型自動下載同步 (`pull`)
    - [x] 一鍵停止腳本 (`stop_dev.bat`)
    - [x] 環境變數安全管理 (`.env` 整合)
- [ ] Godot UI/UX 優化
- [ ] 容器化 (Docker)

## 第四階段：Launcher 控制台
- [x] `launcher/launcher_server.py` - 進程管理 API 伺服器
- [x] `launcher/dashboard.html` - Glassmorphism 風格管理介面
- [x] 多供應商模型切換：LLM (Ollama/OpenAI/Anthropic/Google) + Embedding
- [x] 儀表板功能：啟動/停止、知識庫管理、即時日誌、進入遊戲

- [x] `docs/backend_dev_guide.md` - 後端開發教學文件
- [x] `docs/design_rationale.md` - 技術選型與設計決策說明
- [x] 全系統整合測試與文件同步完成
