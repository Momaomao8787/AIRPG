import chromadb
from chromadb.config import Settings

try:
    # 使用 PersistentClient 替代手動建立 Settings
    client = chromadb.PersistentClient(path="./chroma_db_test")
    print("ChromaDB PersistentClient initialized successfully!")
except Exception as e:
    print(f"Error initializing ChromaDB Client: {e}")
    import traceback
    traceback.print_exc()
