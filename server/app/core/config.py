import os

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

# --- Ollama 模型設定 ---
EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3"

# --- RAG 設定 ---
RETRIEVER_K = 3  # 從向量庫中取回的最相關片段數量
