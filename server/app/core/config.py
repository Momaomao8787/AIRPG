import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

# --- LLM 模型設定 ---
# 供應商選項: "ollama", "openai", "anthropic", "google"
LLM_MODE = os.getenv("LLM_MODE", "ollama") or "ollama"
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3") or "llama3"

# --- 各供應商 API Key ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# --- Embedding 模型設定 ---
# 供應商選項: "ollama", "openai", "google"
EMBED_MODE = os.getenv("EMBED_MODE", "ollama") or "ollama"
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "nomic-embed-text") or "nomic-embed-text"

# --- RAG 設定 ---
RETRIEVER_K = 3  # 從向量庫中取回的最相關片段數量
