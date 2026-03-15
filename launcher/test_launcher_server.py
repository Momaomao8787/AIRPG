import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path
import json

# 設定 PATH 讓 launcher_server.py 可以被 import
import sys
sys.path.insert(0, str(Path(__file__).parent))

import launcher_server

class TestLauncherServer(unittest.TestCase):
    def setUp(self):
        # 使用暫存檔案取代實際的 .env 和 data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Mock paths
        self.original_env_file = launcher_server.ENV_FILE
        launcher_server.ENV_FILE = self.temp_path / ".env"
        
        self.original_data_dir = launcher_server.DATA_DIR
        launcher_server.DATA_DIR = self.temp_path / "data"
        launcher_server.DATA_DIR.mkdir()

        # Mock global state
        launcher_server.backend_logs.clear()
        launcher_server.backend_process = None

    def tearDown(self):
        launcher_server.ENV_FILE = self.original_env_file
        launcher_server.DATA_DIR = self.original_data_dir
        self.temp_dir.cleanup()

    def test_read_env_default(self):
        # 當 ENV 檔案不存在時
        config = launcher_server.read_env()
        self.assertEqual(config.get("LLM_MODE"), "ollama")
        self.assertEqual(config.get("LLM_MODEL_NAME"), "llama3")

    def test_write_and_read_env(self):
        test_config = {
            "LLM_MODE": "openai",
            "LLM_MODEL_NAME": "gpt-4",
            "OPENAI_API_KEY": "test-key"
        }
        launcher_server.write_env(test_config)
        
        # 確認檔案已建立
        self.assertTrue(launcher_server.ENV_FILE.exists())
        
        # 讀取並驗證
        read_config = launcher_server.read_env()
        self.assertEqual(read_config.get("LLM_MODE"), "openai")
        self.assertEqual(read_config.get("LLM_MODEL_NAME"), "gpt-4")
        self.assertEqual(read_config.get("OPENAI_API_KEY"), "test-key")

    def test_get_backend_status_not_running(self):
        status = launcher_server.get_backend_status()
        self.assertFalse(status["running"])

    @patch('subprocess.run')
    def test_stop_backend_already_stopped(self, mock_run):
        # 測試沒有 process 時 stop
        result = launcher_server.stop_backend()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Backend service is not running.")
        self.assertIn("[SYSTEM] Backend service is not running.", launcher_server.backend_logs)

    @patch('launcher_server.platform.system')
    @patch('subprocess.run')
    def test_stop_backend_windows_mock(self, mock_run, mock_system):
        mock_system.return_value = "Windows"
        
        # 建立假的 process
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        # 注意: 這裡故意不設定 pid 屬性看是否有 NoneType 存取錯誤
        # 修正後的 code 應該會有 is not None 之類的檢查, 但原程式碼中如果 mock_proc 沒 pid 則會報 AttributeError
        # 這裡模擬有 pid
        mock_proc.pid = 12345
        launcher_server.backend_process = mock_proc
        
        result = launcher_server.stop_backend()
        self.assertTrue(result["success"])
        mock_run.assert_called_once()
        self.assertIsNone(launcher_server.backend_process)

    def test_log_reader_throttling(self):
        # TODO: 以 mock pipe/stream 重構 log_reader 後補上 throttling 邏輯測試；
        # 或改為用 mock 的 stdout 注入幾行含 % 的內容，只驗證 backend_logs 的更新行為。
        # log_reader 包含無窮迴圈讀取 IO，在單元測試中暫且跳過以防卡死。
        pass

if __name__ == '__main__':
    unittest.main()
