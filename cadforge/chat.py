"""
Chat backend — проксирует сообщения в Claude Code CLI.
Стримит ответы обратно через callback.
"""
import json
import os
import subprocess
import threading


def claude_stream(message, cwd, on_chunk, on_done, on_tool=None, conversation_id=None):
    """Запустить claude CLI и стримить ответ.

    Args:
        message: текст от пользователя
        cwd: рабочая директория проекта
        on_chunk: callback(text) для каждого куска текста
        on_done: callback(full_text) когда завершено
        on_tool: callback(tool_name) при использовании инструмента
        conversation_id: ID предыдущей сессии для продолжения
    """
    def run():
        cmd = [
            "claude",
            "-p", message,
            "--output-format", "stream-json",
            "--verbose",
            "--allowedTools", "Edit", "Write", "Read", "Glob", "Grep", "Bash",
        ]
        if conversation_id:
            cmd.extend(["--resume", conversation_id])

        env = {**os.environ, "CLAUDE_CODE_ENTRYPOINT": "cadforge-chat"}
        # Remove nested session markers so claude CLI doesn't refuse to start
        env.pop("CLAUDECODE", None)
        env.pop("CLAUDE_CODE_SESSION", None)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env,
                text=True,
                bufsize=1,
            )

            full_text = ""
            session_id = None

            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type", "")

                # Extract session ID
                if etype == "system" and event.get("session_id"):
                    session_id = event["session_id"]

                # Text content
                if etype == "assistant" and "message" in event:
                    msg = event["message"]
                    if isinstance(msg, dict):
                        for block in msg.get("content", []):
                            if block.get("type") == "text":
                                text = block["text"]
                                full_text += text
                                on_chunk(text)

                # Content block delta (streaming)
                if etype == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta["text"]
                        full_text += text
                        on_chunk(text)

                # Result message
                if etype == "result":
                    result_text = event.get("result", "")
                    if result_text and not full_text:
                        full_text = result_text
                        on_chunk(result_text)
                    sid = event.get("session_id")
                    if sid:
                        session_id = sid

                # Tool use events
                if etype == "tool_use":
                    tool = event.get("tool", event.get("name", ""))
                    if on_tool:
                        on_tool(tool)
                    else:
                        on_chunk(f"\n[tool: {tool}]\n")

            proc.wait()

            # Check stderr
            stderr = proc.stderr.read()
            if proc.returncode != 0 and stderr:
                on_chunk(f"\n[error: {stderr.strip()}]\n")

            on_done(full_text, session_id)

        except FileNotFoundError:
            on_chunk("[error: claude CLI not found. Install: npm install -g @anthropic-ai/claude-code]")
            on_done("", None)
        except Exception as e:
            on_chunk(f"[error: {e}]")
            on_done("", None)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
