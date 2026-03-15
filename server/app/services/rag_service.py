import codecs
import json
import re
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core import config
from app.core.config import CHROMA_PATH, RETRIEVER_K

# --- System Prompt ---
SYSTEM_PROMPT = """You are an immersive AI Role-playing Assistant. Please answer questions strictly based on the provided "World Background Data".
Please play the role in the first person, maintain the character's tone, and never say things like "I am an AI" or "I don't know".

You MUST respond strictly in the following JSON format without any other text:
{{
  "response": "Character dialogue line",
  "emotion": "Current emotion (neutral/happy/sad/angry/mysterious/surprised)"
}}

[World Background Data]
{context}
"""

USER_TEMPLATE = "{question}"


def _format_docs(docs: list) -> str:
    """將多個文件片段合併為單一字串"""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def _get_embeddings():
    """依 EMBED_MODE 動態選擇 Embedding 模型。"""
    mode = config.EMBED_MODE
    model = config.EMBED_MODEL_NAME
    if mode == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=config.OPENAI_API_KEY, model=model)
    elif mode == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(google_api_key=config.GOOGLE_API_KEY, model=model)
    else:  # 預設 ollama
        return OllamaEmbeddings(model=model)


def _get_llm():
    """依 LLM_MODE 動態選擇語言模型。"""
    mode = config.LLM_MODE
    model = config.LLM_MODEL_NAME
    if mode == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(api_key=config.OPENAI_API_KEY, model=model, temperature=0.7)
    elif mode == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(api_key=config.ANTHROPIC_API_KEY, model=model, temperature=0.7)
    elif mode == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(google_api_key=config.GOOGLE_API_KEY, model=model, temperature=0.7)
    else:  # 預設 ollama
        return ChatOllama(model=model, temperature=0.7)


from typing import Any, cast

_rag_chain: Any = None
_retriever: Any = None


def get_rag_chain():
    """
    初始化並回傳 RAG Chain (Singleton)。
    依 config 中的 LLM_MODE 與 EMBED_MODE 動態選擇模型供應商。
    """
    global _rag_chain, _retriever
    if _rag_chain is not None and _retriever is not None:
        return _rag_chain, _retriever

    # 1. 初始化 Embedding 模型，連接現有的 ChromaDB
    embeddings = _get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )
    _retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})

    # 2. 定義 Prompt 模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_TEMPLATE),
    ])

    # 3. 初始化 LLM
    llm = _get_llm()

    # 4. 使用 LCEL 將各元件串接成 RAG Chain
    _rag_chain = (
        {
            "context": _retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return _rag_chain, _retriever


def query(message: str) -> dict:
    """
    對 RAG Chain 發送查詢，回傳結構化結果。

    Args:
        message: 使用者輸入的訊息文字

    Returns:
        包含 response, emotion, animation_trigger, rag_context 的字典
    """
    rag_chain, retriever = get_rag_chain()

    # 取得 RAG 參考的原始片段
    retrieved_docs = retriever.invoke(message)
    rag_context_texts = [doc.page_content for doc in retrieved_docs]

    # 執行 RAG Chain 取得 LLM 的回應
    raw_output = cast(Any, rag_chain).invoke(message)

    # 嘗試解析 LLM 回傳的 JSON
    cleaned = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = None
    try:
        # 若 LLM 在數字或 null 後多加了尾隨逗號，先移除再解析
        cleaned_fixed = re.sub(r",\s*([}\]])", r"\1", cleaned)
        parsed = json.loads(cleaned_fixed)
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    if parsed is None:
        # 解析失敗時嘗試用正則抽出 "response": "..."，避免把整段 JSON 當成對話顯示
        match = re.search(r'"response"\s*:\s*"((?:[^"\\]|\\.)*)"', cleaned, re.DOTALL)
        if match:
            response_text = codecs.decode(match.group(1), "unicode_escape")
            parsed = {"response": response_text, "emotion": "neutral"}
        else:
            parsed = {"response": raw_output, "emotion": "neutral"}

    resp = parsed.get("response", raw_output)
    if resp is None or not isinstance(resp, str):
        resp = "（角色暫時無法回覆，請再試一次。）"
    emo = parsed.get("emotion", "neutral")
    if emo is None or not isinstance(emo, str):
        emo = "neutral"

    return {
        "response": resp,
        "emotion": emo,
        "animation_trigger": None,
        "rag_context": [],
    }
