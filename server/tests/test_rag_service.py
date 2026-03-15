import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# 將 server 目錄加入 sys.path 以便 import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import rag_service

class TestRagService(unittest.TestCase):
    def setUp(self):
        # 暫存原本的 rag_chain 與 retriever 以免影響其他測試
        self.original_chain = rag_service._rag_chain
        self.original_retriever = rag_service._retriever
        rag_service._rag_chain = None
        rag_service._retriever = None

    def tearDown(self):
        rag_service._rag_chain = self.original_chain
        rag_service._retriever = self.original_retriever

    @patch('app.services.rag_service.config')
    @patch('app.services.rag_service.Chroma')
    @patch('app.services.rag_service.OllamaEmbeddings')
    @patch('app.services.rag_service.ChatOllama')
    def test_get_rag_chain_initialization(self, mock_chat, mock_embed, mock_chroma, mock_config):
        # Mock config
        mock_config.EMBED_MODE = "ollama"
        mock_config.EMBED_MODEL_NAME = "nomic-embed-text"
        mock_config.LLM_MODE = "ollama"
        mock_config.LLM_MODEL_NAME = "llama3"
        mock_config.CHROMA_PATH = "dummy_path"
        mock_config.RETRIEVER_K = 2

        # Mock Chroma vectorstore behavior
        mock_vectorstore_instance = MagicMock()
        mock_chroma.return_value = mock_vectorstore_instance
        # 修正：回傳 MagicMock 而非 string，確保 LCEL `_retriever | _format_docs` 支援 `__or__`
        dummy_retriever = MagicMock()
        mock_vectorstore_instance.as_retriever.return_value = dummy_retriever

        chain, retriever = rag_service.get_rag_chain()
        
        # 驗證 Retriever 和 Chain 是否有成功被賦值或組裝
        self.assertEqual(retriever, dummy_retriever)
        self.assertIsNotNone(chain)
        
        # 確認單例模式：再次呼叫不應重新初始化
        chain2, retriever2 = rag_service.get_rag_chain()
        self.assertIs(chain, chain2)
        mock_chroma.assert_called_once()

    @patch('app.services.rag_service.get_rag_chain')
    def test_query_success_json_response(self, mock_get_chain):
        # Mock chain 執行
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = '{"response": "Hello", "emotion": "happy", "animation_trigger": "nod"}'
        
        # Mock retriever 執行
        mock_retriever = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "World Context"
        mock_retriever.invoke.return_value = [mock_doc]

        mock_get_chain.return_value = (mock_chain, mock_retriever)

        result = rag_service.query("Hi")
        self.assertEqual(result["response"], "Hello")
        self.assertEqual(result["emotion"], "happy")
        self.assertIsNone(result["animation_trigger"])
        self.assertEqual(result["rag_context"], [])

    @patch('app.services.rag_service.get_rag_chain')
    def test_query_fallback_plain_text(self, mock_get_chain):
        # 模擬 LLM 沒回傳標準 JSON 格式
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "This is a plain text response without JSON format."
        
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = []

        mock_get_chain.return_value = (mock_chain, mock_retriever)

        result = rag_service.query("Tell me a story")
        self.assertEqual(result["response"], "This is a plain text response without JSON format.")
        self.assertEqual(result["emotion"], "neutral")
        self.assertIsNone(result["animation_trigger"])
        self.assertEqual(result["rag_context"], [])

if __name__ == '__main__':
    unittest.main()
