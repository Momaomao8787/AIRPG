import json
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core import config
from app.core.config import CHROMA_PATH, RETRIEVER_K

# --- 系統提示詞 ---
SYSTEM_PROMPT = """你是一個沉浸式 AI 角色扮演助理。請嚴格依照以下提供的「世界觀背景資料」來回答問題。
請以第一人稱扮演角色，保持角色的說話語氣，切勿說出「我是 AI」或「我不知道」等出戲的話語。

請務必以以下 JSON 格式回應，不要加入任何其他文字：
{{
  "response": "角色的對話台詞",
  "emotion": "當前情緒 (neutral/happy/sad/angry/mysterious/surprised 之一)",
  "animation_trigger": "動畫指令 (idle/talk/nod/shake_head 之一，或 null)"
}}

【世界觀背景資料】
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


def get_rag_chain():
    """
    初始化並回傳 RAG Chain。
    依 config 中的 LLM_MODE 與 EMBED_MODE 動態選擇模型供應商。
    """
    # 1. 初始化 Embedding 模型，連接現有的 ChromaDB
    embeddings = _get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})

    # 2. 定義 Prompt 模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_TEMPLATE),
    ])

    # 3. 初始化 LLM
    llm = _get_llm()

    # 4. 使用 LCEL 將各元件串接成 RAG Chain
    rag_chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


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
    raw_output = rag_chain.invoke(message)

    # 嘗試解析 LLM 回傳的 JSON
    try:
        # 有時 LLM 會在 JSON 外包裹 markdown code block，先清理
        cleaned = raw_output.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        # 若解析失敗，直接將原始文字作為回應
        parsed = {
            "response": raw_output,
            "emotion": "neutral",
            "animation_trigger": None,
        }

    return {
        "response": parsed.get("response", raw_output),
        "emotion": parsed.get("emotion", "neutral"),
        "animation_trigger": parsed.get("animation_trigger"),
        "rag_context": rag_context_texts,
    }
