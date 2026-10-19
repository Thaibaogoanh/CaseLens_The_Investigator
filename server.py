#!/usr/bin/env python3
"""Dependency-free Python 3.11+ app server for the public, synthetic-data demo."""
import json
import logging
import mimetypes
import os
import socket
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from app.engine import Investigator, REQUEST_AI
from app.fixtures import public_cases
from app.validation import AppError
from app.intake import normalize

ROOT = Path(__file__).resolve().parent


def load_env():
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


class RateLimiter:
    def __init__(self):
        self.entries = OrderedDict()
        self.lock = threading.Lock()

    def allow(self, address):
        now = time.monotonic()
        with self.lock:
            # Reverse proxy clients may share a bucket; do not trust arbitrary X-Forwarded-For.
            hits = [at for at in self.entries.pop(address, []) if now - at < 60]
            allowed = len(hits) < 15
            if allowed:
                hits.append(now)
            self.entries[address] = hits
            while len(self.entries) > 1000:
                self.entries.popitem(last=False)
            return allowed


class Handler(BaseHTTPRequestHandler):
    engine = None
    limiter = RateLimiter()
    server_version = "CaseLens/2.3.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, fmt, *args):
        # Do not log source bodies, questions, query parameters or credentials.
        logging.info("%s %s", getattr(self, "command", "NO_REQUEST"), urlsplit(getattr(self, "path", "")).path)

    def send_bytes(self, status, body, content_type):
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, TimeoutError):
            self.close_connection = True
            logging.info("Client disconnected before response completed")

    def json_response(self, status, data):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            return self.json_response(200, {"status": "ok"})
        if path == "/api/config":
            return self.json_response(200, self.engine.config())
        if path == "/api/cases":
            return self.json_response(200, {"cases": public_cases()})
        static = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/extensions.js": "extensions.js", "/styles.css": "styles.css", "/favicon.svg": "favicon.svg"}
        if path in static:
            file = ROOT / "static" / static[path]
            mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            return self.send_bytes(200, file.read_bytes(), mime + ("; charset=utf-8" if mime.startswith("text/") or mime == "application/javascript" else ""))
        self.json_response(404, {"error": "Not found."})

    def do_POST(self):
        try:
            if urlsplit(self.path).path not in ("/api/investigate", "/api/ask", "/api/review", "/api/normalize", "/api/inspect"):
                raise AppError("Not found.", 404)
            origin = self.headers.get("Origin")
            if origin:
                parsed = urlsplit(origin)
                allowed = os.environ.get("PUBLIC_ORIGIN", "").rstrip("/")
                if not (origin == allowed or (parsed.scheme in ("http", "https") and parsed.netloc == self.headers.get("Host"))):
                    raise AppError("Cross-origin requests are not allowed.", 403)
            if not self.headers.get("Content-Type", "").lower().startswith("application/json"):
                raise AppError("Content-Type must be application/json.", 415)
            if not self.limiter.allow(self.client_address[0]):
                raise AppError("Too many requests. Please wait one minute.", 429)
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise AppError("Invalid Content-Length.")
            limit = 500000 if urlsplit(self.path).path in ('/api/review', '/api/inspect') else 250000
            if not 0 < size <= limit:
                raise AppError(f"Request body must be between 1 and {limit:,} bytes.", 413)
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise AppError("Incomplete request body.")
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise AppError("The request body must be valid UTF-8 JSON.")
            handlers = {'/api/investigate': self.engine.run, '/api/ask': self.engine.ask,
                        '/api/review': self.engine.review, '/api/normalize': normalize,
                        '/api/inspect': self.engine.inspect_snapshot}
            override = None
            if self.headers.get("X-AI-Key"):
                provider = self.headers.get("X-AI-Provider", "")
                model = self.headers.get("X-AI-Model", "")
                key = self.headers.get("X-AI-Key", "")
                import re
                if provider not in ("gemini", "openai") or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", model):
                    raise AppError("Select a valid provider and model for your key.")
                if len(key) > 1024 or not key.isascii() or any(ord(c) < 33 for c in key):
                    raise AppError("Invalid API key format.")
                override = dict(provider=provider, model=model, key=key)
            token = REQUEST_AI.set(override)
            try:
                result = handlers[urlsplit(self.path).path](payload)
            finally:
                REQUEST_AI.reset(token)
            self.json_response(200, result)
        except AppError as exc:
            self.json_response(exc.status, {"error": str(exc)})
        except (BrokenPipeError, ConnectionResetError, socket.timeout):
            return
        except Exception:
            logging.error("Unexpected request failure; no request content was logged.")
            self.json_response(500, {"error": "An unexpected server error occurred. Please retry."})


def create_server(host="127.0.0.1", port=8000):
    Handler.engine = Investigator()
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    load_env()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = create_server(host, port)
    print(f"CaseLens ready: http://{host}:{port} (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
