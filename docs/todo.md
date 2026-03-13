# Project Tasks

## 第一階段：後端核心 (已完成)
- [x] Python 環境配置 (venv)
- [x] FastAPI 核心實做
    - [x] 基礎伺服器架構 (`main.py`)
    - [x] 健康檢查端點 (`/health`)
    - [x] `/chat` 對話端點 (`POST /api/v1/chat/`)
- [x] RAG 引擎整合 (已更換為高效能 nomic-embed-text 模型)
- [x] 知識庫處理 (已支援 .md 並提供開發邏輯教學)
- [x] 對話 API 實作
    - [x] `core/config.py` - 集中設定管理
    - [x] `schemas/chat.py` - Pydantic 資料模型
    - [x] `services/rag_service.py` - RAG Chain (LCEL + JSON 輸出)
    - [x] `api/v1/endpoints/chat.py` - 端點定義

## 第二階段：開發工具與管理 (已完成)
- [x] **開發體驗優化**
    - [x] 一鍵啟動腳本 (`start_dev.bat`)
    - [x] 一鍵停止腳本 (`stop_dev.bat`)
    - [x] Ollama 自動診斷與啟動服務
    - [x] 模型自動下載同步 (`pull`)
    - [x] 環境變數安全管理 (`.env` 整合)
- [x] **Launcher 控制台**
    - [x] `launcher/launcher_server.py` - 進程管理 API 伺服器
    - [x] `launcher/dashboard.html` - Glassmorphism 風格管理介面
    - [x] 多供應商模型切換 (LLM + Embedding)
    - [x] 儀表板面板：啟動/停止、日誌檢視、進入遊戲

## 第三階段：前端整合與容器化 (進行中 - 第一版目標)
- [ ] **Godot 基礎建置**
    - [ ] 基礎通訊模組 (HTTPRequest 整合)
    - [ ] 基本 UI 介面 (對話框、輸入框)
- [ ] **Docker 部署**
    - [ ] 撰寫 Dockerfile (後端 + Launcher)
    - [ ] 撰寫 docker-compose.yml
- [ ] 全系統端到端 (E2E) 測試

## 第四階段：進階功能開發
- [ ] **長期記憶支援**
    - [ ] SQLite 整合儲存對話歷史
    - [ ] 歷史上下文檢索邏輯
- [ ] **對話檢索優化**
    - [ ] RAG 精度調優 (Chunking strategy, Re-ranking)
- [ ] **知識庫管理介面**
    - [ ] Launcher 加入上傳/刪除世界觀文件功能

## 第五階段：體驗展演優化
- [ ] **Godot UI/UX 優化**
  - [ ] 字體與樣式精雕細琢
  - [ ] 對話打字機動效與表情切換動效
- [ ] **串流回傳 (Streaming)**
  - [ ] Backend 實作 SSE
  - [ ] Godot 實作非同步接收
- [ ] **指令解析 (State-Driven)**
  - [ ] AI 回傳 JSON 控制遊戲內特定事件 (如 BGM 切換、背景更換)

---
- [x] `docs/backend_dev_guide.md` - 後端開發教學文件
- [x] `docs/design_rationale.md` - 技術選型與設計決策說明
- [x] `docs/rag_dev_guide.md` - RAG 引擎開發指南
- [x] `docs/memory_strategy.md` - 長期記憶策略規劃
