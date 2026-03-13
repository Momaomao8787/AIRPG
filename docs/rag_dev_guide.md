# AIRPA: RAG 知識導入開發邏輯教學

本技術文件旨在指導如何透過 RAG（檢索增強生成）技術，將外部世界觀設定整合進 AI 角色扮演系統中。

## 0. 專案導入：為何需要 RAG？

在開發 **AIRPA (AI Immersive Role-Playing Agent)** 時，我們的核心目標是讓 AI 具備「特定世界觀」的記憶。
*   **傳統 LLM 的限制**：模型對本地世界觀一無所知，容易產生幻覺。
*   **RAG 的解決方案**：在 AI 回答前，先從您的「設定集」中檢索相關內容，作為上下文（Context）餵給模型。
*   **與 Godot 的連結**：Godot 發送請求 -> 後端執行 RAG 檢索 -> LLM 生成具備設定依據的回應 -> Godot 展演。

---

## 1. 知識導入的四個核心階段

以下我們根據 [server/app/rag/ingest.py](file:///c:/Users/user/Documents/DevilCatGames/AIRPG/server/app/rag/ingest.py) 的邏輯進行拆解：

### 第一階段：資料載入 (Loading)
我們使用 `DirectoryLoader` 讀取 `server/data/` 目錄。
*   **邏輯**：系統會掃描目錄，將 `.md` 或 `.txt` 檔案的純文字內容讀入記憶體。
*   **關鍵修正**：原本腳本僅支援 `.txt`，我們已修正為支援 `.md`，以符合專案目前的設定格式。

### 第二階段：文本切塊 (Splitting)
由於 LLM 的 Context Window 有長度限制，我們不能一次餵入萬字長文。
*   **Chunk Size (500)**：每個段落限制在 500 字，確保資訊密度適中。
*   **Chunk Overlap (50)**：段落與段落之間重疊 50 字，防止重要資訊（如人名、年代）在切塊邊界被截斷。

### 第三階段：向量化 (Embedding)
電腦不理解文字，但理解數字。
*   **概念**：使用 `OllamaEmbeddings` 將文字轉換為一組高維度向量（一串數字）。
*   **意義**：語意相近的文字（例如：「精靈」與「耳朵尖尖的人」），在向量空間中的距離會非常接近。

### 第四階段：持久化儲存 (Vector Store)
我們使用 **ChromaDB** 作為向量資料庫。
*   **邏輯**：將切好的塊與對應的向量存入 `chroma_db` 資料夾。
*   **用途**：未來對話時，我們只需將使用者的問題向量化，就能在資料庫中快速「搜尋」到語意最接近的知識塊。

---

## 2. 常見環境問題排解

在某些環境中，`chromadb` 可能會與 `pydantic` 產生版本衝突（例如：`ConfigError`），這是因為 `chromadb` 內部使用了較舊的 Pydantic v1 相容層。

**解決建議：**
1.  確保 `pip install "pydantic<2.10"` 以維持相容性。
2.  若環境鎖定，可考慮使用 `FAISS` 作為輕量級替代方案。

## 3. 下一步行動
知識導入完成後，下一步是在 `FastAPI` 中實作 `/chat` 端點，將「使用者輸入」轉化為「向量搜尋」，再產出結果！
