import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 設定路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

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

    # 3. 初始化 Embedding 模型 (nomic-embed-text)
    print("正在初始化 Embedding 模型 (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

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