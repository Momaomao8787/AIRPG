import os
import sys
from pathlib import Path

# 以腳本執行時確保可 import app（cwd 為 server 時由 launcher 啟動則無需此段）
_SERVER_DIR = Path(__file__).resolve().parent.parent.parent
if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

from dotenv import load_dotenv
load_dotenv()

from app.core import config
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


def get_embeddings():
    """Dynamically choose Embedding model based on config.EMBED_MODE."""
    if config.EMBED_MODE == "openai":
        from langchain_openai import OpenAIEmbeddings
        print(f"Using OpenAI Embeddings: {config.EMBED_MODEL_NAME}")
        return OpenAIEmbeddings(api_key=config.OPENAI_API_KEY, model=config.EMBED_MODEL_NAME)
    elif config.EMBED_MODE == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print(f"Using Google Embeddings: {config.EMBED_MODEL_NAME}")
        return GoogleGenerativeAIEmbeddings(google_api_key=config.GOOGLE_API_KEY, model=config.EMBED_MODEL_NAME)
    else:
        from langchain_ollama import OllamaEmbeddings
        print(f"Using Ollama Embeddings: {config.EMBED_MODEL_NAME}")
        return OllamaEmbeddings(model=config.EMBED_MODEL_NAME)

def main():
    # 1. Load documents
    print(f"Loading documents from {config.DATA_PATH}...")
    loader = DirectoryLoader(
        config.DATA_PATH,
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
    print(f"Building vector database at {config.CHROMA_PATH}...")

    if os.path.exists(config.CHROMA_PATH):
        import shutil
        shutil.rmtree(config.CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=config.CHROMA_PATH
    )
    print("Knowledge base built successfully.")

if __name__ == "__main__":
    main()