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

## 第三階段：體驗優化與部署
- [ ] Godot UI/UX 優化
- [ ] 容器化 (Docker)

## 文件
- [x] `dev_plan/backend_dev_guide.md` - 後端開發教學文件

