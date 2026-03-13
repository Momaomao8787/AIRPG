import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# 載入 .env 設定
load_dotenv()

# 設定路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

# 讀取 Embedding 設定
EMBED_MODE = os.getenv("EMBED_MODE", "ollama") or "ollama"
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "nomic-embed-text") or "nomic-embed-text"


def get_embeddings():
    """依據 EMBED_MODE 動態選擇 Embedding 模型。"""
    if EMBED_MODE == "openai":
        from langchain_openai import OpenAIEmbeddings
        print(f"使用 OpenAI Embeddings: {EMBED_MODEL_NAME}")
        return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY", ""), model=EMBED_MODEL_NAME)
    elif EMBED_MODE == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print(f"使用 Google Embeddings: {EMBED_MODEL_NAME}")
        return GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY", ""), model=EMBED_MODEL_NAME)
    else:
        from langchain_ollama import OllamaEmbeddings
        print(f"使用 Ollama Embeddings: {EMBED_MODEL_NAME}")
        return OllamaEmbeddings(model=EMBED_MODEL_NAME)

def main():
    # 1. 載入文件 (讀取 data 目錄下所有 .md 與 .txt 檔案)
    print(f"正在從 {DATA_PATH} 載入文件...")
    # 支援多種常用文本格式
    loader = DirectoryLoader(
        DATA_PATH, 
        glob="**/*.md",     
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf8'}
    )
    documents = loader.load()
    
    # 2. 文本切塊 (將長文章切成好消化的小段落)
    print("正在進行文本切塊...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 每個區塊 500 字
        chunk_overlap=50,      # 前後區塊重疊 50 字，保持上下文連貫
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"已切分為 {len(chunks)} 個區塊")

    # 3. 初始化 Embedding 模型
    embeddings = get_embeddings()

    # 4. 存入 ChromaDB (建立向量資料庫)
    print(f"正在建立向量資料庫並存至 {CHROMA_PATH}...")
    
    # 如果資料庫已存在就先刪除（清空舊資料）
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    print("知識庫建置完成")

if __name__ == "__main__":
    main()