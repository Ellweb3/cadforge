"""
Dev server — HTTP для viewer + WebSocket для hot reload.
"""
import asyncio
import http.server
import json
import os
import threading
import socketserver
from pathlib import Path


# WebSocket connections
_ws_clients = set()
_event_loop = None
_project_root = None


class ViewerHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler для viewer и dist файлов."""

    def __init__(self, *args, root_dir=None, dist_dir=None, **kwargs):
        self.root_dir = root_dir
        self.dist_dir = dist_dir
        super().__init__(*args, **kwargs)

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.glb': 'model/gltf-binary',
        '.gltf': 'model/gltf+json',
        '.stl': 'application/octet-stream',
        '.wasm': 'application/wasm',
    }

    def translate_path(self, path):
        """Route /dist/* к dist директории, остальное к viewer."""
        # Убираем query string
        clean = path.split("?")[0].split("#")[0]
        if clean.startswith("/dist/"):
            rel = clean[6:]
            return os.path.join(self.dist_dir, rel)
        if clean.startswith("/api/"):
            return clean  # API routes handled separately
        # Viewer static files
        viewer_dir = os.path.join(self.root_dir, "viewer")
        if clean == "/" or clean == "":
            return os.path.join(viewer_dir, "index.html")
        return os.path.join(viewer_dir, clean.lstrip("/"))

    def do_GET(self):
        if self.path == "/api/status":
            self._json_response({"status": "running", "version": "0.3.0"})
            return
        if self.path == "/api/manifest":
            manifest_path = os.path.join(self.dist_dir, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    data = json.load(f)
                self._json_response(data)
            else:
                self._json_response({"error": "no build yet"}, 404)
            return
        if self.path == "/api/export/cadforge":
            self._export_cadforge()
            return
        if self.path == "/api/export/freecad-script":
            self._export_freecad_script()
            return
        super().do_GET()

    def _export_cadforge(self):
        """Экспорт .cadforge — ZIP с проектом."""
        import zipfile
        import io
        buf = io.BytesIO()
        project_dir = os.path.join(self.root_dir, "project")
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            # cadforge.toml
            toml_path = os.path.join(self.root_dir, "cadforge.toml")
            if os.path.exists(toml_path):
                zf.write(toml_path, "cadforge.toml")
            # project/ files
            for dirpath, _, filenames in os.walk(project_dir):
                for fn in filenames:
                    if fn.endswith(('.py', '.png', '.jpg')):
                        full = os.path.join(dirpath, fn)
                        arc = os.path.relpath(full, self.root_dir)
                        zf.write(full, arc)
            # dist/model.glb
            glb = os.path.join(self.dist_dir, "model.glb")
            if os.path.exists(glb):
                zf.write(glb, "dist/model.glb")
            # manifest
            mf = os.path.join(self.dist_dir, "manifest.json")
            if os.path.exists(mf):
                zf.write(mf, "dist/manifest.json")
        data = buf.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", "attachment; filename=project.cadforge")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _export_freecad_script(self):
        """Экспорт standalone FreeCAD Python скрипт."""
        project_dir = os.path.join(self.root_dir, "project")
        parts = []
        parts.append("#!/usr/bin/env freecadcmd")
        parts.append("# CadForge standalone build script")
        parts.append("# Run: freecadcmd this_script.py")
        parts.append("import sys, os")
        parts.append(f"sys.path.insert(0, {repr(self.root_dir)})")
        parts.append("import FreeCAD")
        parts.append("doc = FreeCAD.newDocument('CadForge')")
        # Read module sequence from cadforge.toml
        toml_path = os.path.join(self.root_dir, "cadforge.toml")
        modules = []
        if os.path.exists(toml_path):
            with open(toml_path) as f:
                for line in f:
                    line = line.strip().strip(',').strip('"').strip("'")
                    if '.' in line and not line.startswith('#') and not line.startswith('['):
                        if all(c.isalnum() or c in '._' for c in line):
                            modules.append(line)
        for mod in modules:
            parts.append(f"from project.{mod} import build as build_{mod.replace('.', '_')}")
            parts.append(f"build_{mod.replace('.', '_')}(doc)")
        parts.append("doc.recompute()")
        parts.append("# Save as .FCStd:")
        parts.append("# doc.saveAs('output.FCStd')")
        parts.append("print('Build complete:', len(doc.Objects), 'objects')")
        script = "\n".join(parts) + "\n"
        data = script.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/x-python")
        self.send_header("Content-Disposition", "attachment; filename=build.py")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # Тихий режим


def make_handler(root_dir, dist_dir):
    """Создать handler с привязкой к директориям."""
    def handler(*args, **kwargs):
        return ViewerHandler(*args, root_dir=root_dir, dist_dir=dist_dir, **kwargs)
    return handler


def start_http(root_dir, dist_dir, port=3000):
    """Запустить HTTP сервер в фоновом потоке."""
    global _project_root
    _project_root = root_dir
    handler = make_handler(root_dir, dist_dir)
    httpd = socketserver.TCPServer(("", port), handler)
    httpd.allow_reuse_address = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"  HTTP server: http://localhost:{port}")
    return httpd


_chat_sessions = {}  # ws -> session_id


async def _ws_handler(websocket):
    """WebSocket handler — регистрирует клиента, обрабатывает чат."""
    _ws_clients.add(websocket)
    try:
        async for msg in websocket:
            try:
                data = json.loads(msg)
                msg_type = data.get("type")

                if msg_type == "request_build":
                    await websocket.send(json.dumps({"type": "build_queued"}))

                elif msg_type == "chat":
                    await _handle_chat(websocket, data)

            except json.JSONDecodeError:
                pass
    finally:
        _ws_clients.discard(websocket)
        _chat_sessions.pop(websocket, None)


async def _handle_chat(websocket, data):
    """Обработать chat сообщение — запустить claude CLI."""
    from .chat import claude_stream

    message = data.get("message", "").strip()
    if not message:
        return

    # Отправить подтверждение
    await websocket.send(json.dumps({
        "type": "chat_start",
    }))

    loop = asyncio.get_event_loop()
    session_id = _chat_sessions.get(websocket)

    def on_chunk(text):
        """Стримить текст в WebSocket."""
        asyncio.run_coroutine_threadsafe(
            websocket.send(json.dumps({
                "type": "chat_delta",
                "text": text,
            })),
            loop,
        )

    def on_tool(tool_name):
        """Уведомить о вызове инструмента."""
        asyncio.run_coroutine_threadsafe(
            websocket.send(json.dumps({
                "type": "chat_tool",
                "tool": tool_name,
            })),
            loop,
        )

    def on_done(full_text, new_session_id):
        """Завершение ответа."""
        if new_session_id:
            _chat_sessions[websocket] = new_session_id
        asyncio.run_coroutine_threadsafe(
            websocket.send(json.dumps({
                "type": "chat_done",
                "session_id": new_session_id,
            })),
            loop,
        )

    cwd = _project_root or os.getcwd()
    claude_stream(message, cwd, on_chunk, on_done, on_tool, session_id)


def notify_clients(event_type, data=None):
    """Отправить событие всем подключенным клиентам."""
    msg = json.dumps({"type": event_type, **(data or {})})

    if _event_loop and _ws_clients:
        for ws in list(_ws_clients):
            asyncio.run_coroutine_threadsafe(ws.send(msg), _event_loop)


async def _run_ws(port):
    """Запустить WebSocket сервер."""
    global _event_loop
    import websockets
    _event_loop = asyncio.get_event_loop()
    async with websockets.serve(_ws_handler, "localhost", port):
        print(f"  WebSocket server: ws://localhost:{port}")
        await asyncio.Future()  # run forever


def start_websocket(port=3001):
    """Запустить WebSocket в фоновом потоке."""
    def run():
        asyncio.run(_run_ws(port))

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
