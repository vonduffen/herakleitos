"""Local GUI for talking to the PoC student model.

Serves the chat UI and proxies /api/chat to the mlx_lm OpenAI-compatible
server (SSE streaming passthrough). If the model server isn't running, it is
spawned automatically with the round-2 adapter.

Run:  uv run python harness/serve_ui.py          # UI on :8765, model on :8080
"""

from __future__ import annotations

import http.client
import json
import socket
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

UI_PORT = 8765
MODEL_PORT = 8080
MODEL = "mlx-community/Qwen3-1.7B-4bit"
ADAPTER = Path(__file__).resolve().parent.parent / "training" / "adapters" / "poc2"
MLX_LM = "/Users/m4/miniconda3/bin/mlx_lm"
UI_HTML = Path(__file__).resolve().parent / "ui.html"

STUDENT_SYSTEM = (
    "You reason in processes, exchanges, and held tensions: what persists "
    "through change, how opposites depend on each other, what tension holds a "
    "thing together. Plain, concrete prose, 2-6 sentences unless asked "
    "otherwise. No philosopher quotes, no 'flux', no oracular voice. /no_think"
)


def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ensure_model_server() -> None:
    if _port_open(MODEL_PORT):
        print(f"model server already up on :{MODEL_PORT}")
        return
    print(f"starting mlx_lm server ({MODEL} + {ADAPTER.name}) on :{MODEL_PORT} ...")
    subprocess.Popen(
        [MLX_LM, "server", "--model", MODEL, "--adapter-path", str(ADAPTER),
         "--port", str(MODEL_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        if _port_open(MODEL_PORT):
            print("model server up")
            return
        time.sleep(1)
    sys.exit("model server failed to start")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quiet
        pass

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            body = UI_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/health":
            ok = _port_open(MODEL_PORT)
            body = json.dumps({"model_up": ok, "model": MODEL, "adapter": "poc2"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(length) or b"{}")
        messages = [{"role": "system", "content": STUDENT_SYSTEM}]
        messages += [
            m for m in req.get("messages", []) if m.get("role") in ("user", "assistant")
        ][-12:]

        upstream = http.client.HTTPConnection("127.0.0.1", MODEL_PORT, timeout=300)
        upstream.request(
            "POST",
            "/v1/chat/completions",
            body=json.dumps(
                {
                    "model": MODEL,
                    "messages": messages,
                    "temperature": float(req.get("temperature", 0.7)),
                    "max_tokens": 700,
                    "stream": True,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        resp = upstream.getresponse()

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            while True:
                chunk = resp.read(256)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            upstream.close()


def main() -> None:
    ensure_model_server()
    server = ThreadingHTTPServer(("127.0.0.1", UI_PORT), Handler)
    print(f"student UI on http://localhost:{UI_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
