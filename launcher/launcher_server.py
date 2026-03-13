#!/usr/bin/env python3
"""
AIRPG Launcher Server
輕量級控制台伺服器，負責管理後端服務、讀寫設定與串流日誌。
"""
import os
import sys
import json
import subprocess
import signal
import threading
import time
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# --- 路徑設定 ---
LAUNCHER_DIR = Path(__file__).parent
PROJECT_ROOT = LAUNCHER_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
ENV_FILE = SERVER_DIR / ".env"
DATA_DIR = SERVER_DIR / "data"
LAUNCHER_PORT = 8080

# --- 全域進程狀態 ---
backend_process = None
backend_logs = []
log_lock = threading.Lock()
MAX_LOG_LINES = 200


def read_env() -> dict:
    """讀取 server/.env 檔案為字典。"""
    config = {
        "LLM_MODE": "ollama",
        "LLM_MODEL_NAME": "llama3",
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "GOOGLE_API_KEY": "",
        "EMBED_MODE": "ollama",
        "EMBED_MODEL_NAME": "nomic-embed-text",
    }
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config


def write_env(config: dict):
    """將設定字典寫回 server/.env 檔案。"""
    lines = [
        "# AIRPG 環境設定 (由 Launcher 自動生成)\n\n",
        "# --- LLM 設定 ---\n",
        f"LLM_MODE={config.get('LLM_MODE', 'ollama')}\n",
        f"LLM_MODEL_NAME={config.get('LLM_MODEL_NAME', 'llama3')}\n",
        f"OPENAI_API_KEY={config.get('OPENAI_API_KEY', '')}\n",
        f"ANTHROPIC_API_KEY={config.get('ANTHROPIC_API_KEY', '')}\n",
        f"GOOGLE_API_KEY={config.get('GOOGLE_API_KEY', '')}\n\n",
        "# --- Embedding 設定 ---\n",
        f"EMBED_MODE={config.get('EMBED_MODE', 'ollama')}\n",
        f"EMBED_MODEL_NAME={config.get('EMBED_MODEL_NAME', 'nomic-embed-text')}\n",
    ]
    ENV_FILE.write_text("".join(lines), encoding="utf-8")


def get_backend_status() -> dict:
    """確認後端伺服器是否正在運行。"""
    global backend_process
    running = backend_process is not None and backend_process.poll() is None
    return {"running": running}


def start_backend():
    """啟動後端伺服器。"""
    global backend_process, backend_logs
    if backend_process and backend_process.poll() is None:
        return {"success": False, "message": "後端已在運行中。"}

    bat_file = SERVER_DIR / "run_server.bat"
    if not bat_file.exists():
        return {"success": False, "message": f"找不到 {bat_file}"}

    with log_lock:
        backend_logs.clear()

    def log_reader(proc):
        for line in iter(proc.stdout.readline, b""):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            with log_lock:
                backend_logs.append(decoded)
                if len(backend_logs) > MAX_LOG_LINES:
                    backend_logs.pop(0)
        proc.stdout.close()

    backend_process = subprocess.Popen(
        ["cmd.exe", "/c", str(bat_file)],
        cwd=str(SERVER_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
    )
    threading.Thread(target=log_reader, args=(backend_process,), daemon=True).start()
    return {"success": True, "message": "後端服務啟動中..."}


def stop_backend():
    """停止後端伺服器。"""
    global backend_process
    if not backend_process or backend_process.poll() is not None:
        return {"success": False, "message": "後端目前未在運行。"}

    if platform.system() == "Windows":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)],
                       capture_output=True)
    else:
        os.kill(backend_process.pid, signal.SIGTERM)

    backend_process = None
    return {"success": True, "message": "後端服務已停止。"}


def run_ingest():
    """執行知識庫重建腳本。"""
    ingest_script = SERVER_DIR / "app" / "rag" / "ingest.py"
    if not ingest_script.exists():
        return {"success": False, "message": "找不到 ingest.py"}

    venv_python = SERVER_DIR / "venv" / "Scripts" / "python.exe"
    python_exec = str(venv_python) if venv_python.exists() else sys.executable

    def _run():
        proc = subprocess.Popen(
            [python_exec, str(ingest_script)],
            cwd=str(SERVER_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for line in iter(proc.stdout.readline, b""):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            with log_lock:
                backend_logs.append(f"[ingest] {decoded}")
                if len(backend_logs) > MAX_LOG_LINES:
                    backend_logs.pop(0)
        proc.stdout.close()
        with log_lock:
            backend_logs.append("[ingest] 知識庫更新完畢！")

    threading.Thread(target=_run, daemon=True).start()
    return {"success": True, "message": "知識庫更新中，請查看日誌。"}


def list_data_files() -> list:
    """列出 data/ 目錄中的文件。"""
    if not DATA_DIR.exists():
        return []
    return [f.name for f in DATA_DIR.iterdir() if f.is_file()]


class LauncherHandler(BaseHTTPRequestHandler):
    """Launcher HTTP 請求處理器。"""

    def log_message(self, format, *args):
        pass  # 靜默模式

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, filepath: Path, content_type: str):
        if not filepath.exists():
            self.send_response(404)
            self.end_headers()
            return
        body = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.serve_file(LAUNCHER_DIR / "dashboard.html", "text/html; charset=utf-8")
        elif path == "/api/status":
            status = get_backend_status()
            status["files"] = list_data_files()
            self.send_json(status)
        elif path == "/api/config":
            self.send_json(read_env())
        elif path == "/api/logs":
            with log_lock:
                self.send_json({"logs": list(backend_logs)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/api/config":
            current = read_env()
            current.update(data)
            write_env(current)
            self.send_json({"success": True, "message": "設定已儲存。"})
        elif path == "/api/start":
            self.send_json(start_backend())
        elif path == "/api/stop":
            self.send_json(stop_backend())
        elif path == "/api/ingest":
            self.send_json(run_ingest())
        else:
            self.send_response(404)
            self.end_headers()


def main():
    print(f"[AIRPG Launcher] 啟動中... http://localhost:{LAUNCHER_PORT}")
    server = HTTPServer(("0.0.0.0", LAUNCHER_PORT), LauncherHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[AIRPG Launcher] 已關閉。")
        server.shutdown()


if __name__ == "__main__":
    main()
