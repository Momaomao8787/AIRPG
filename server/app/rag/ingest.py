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
    """Dynamically choose Embedding model based on EMBED_MODE."""
    if EMBED_MODE == "openai":
        from langchain_openai import OpenAIEmbeddings
        print(f"Using OpenAI Embeddings: {EMBED_MODEL_NAME}")
        return OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY", ""), model=EMBED_MODEL_NAME)
    elif EMBED_MODE == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print(f"Using Google Embeddings: {EMBED_MODEL_NAME}")
        return GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY", ""), model=EMBED_MODEL_NAME)
    else:
        from langchain_ollama import OllamaEmbeddings
        print(f"Using Ollama Embeddings: {EMBED_MODEL_NAME}")
        return OllamaEmbeddings(model=EMBED_MODEL_NAME)

def main():
    # 1. Load documents
    print(f"Loading documents from {DATA_PATH}...")
    loader = DirectoryLoader(
        DATA_PATH, 
        glob="**/*.md",     
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf8'}
    )
    documents = loader.load()
    
    # 2. Split text
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # 3. Initialize Embedding
    embeddings = get_embeddings()

    # 4. Save to ChromaDB
    print(f"Building vector database at {CHROMA_PATH}...")
    
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    print("Knowledge base built successfully.")

if __name__ == "__main__":
    main()