"""
File watcher — следит за изменениями в project/ и триггерит пересборку.
"""
import os
import time
import threading
from pathlib import Path


class ProjectWatcher:
    """Следит за .py файлами и вызывает callback при изменениях."""

    def __init__(self, watch_dirs, callback, debounce_ms=500):
        self.watch_dirs = watch_dirs
        self.callback = callback
        self.debounce = debounce_ms / 1000.0
        self._running = False
        self._thread = None
        self._file_mtimes = {}
        self._pending = False
        self._last_trigger = 0

    def start(self):
        """Запустить наблюдение в фоновом потоке."""
        self._running = True
        self._scan_mtimes()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        dirs = ", ".join(str(d) for d in self.watch_dirs)
        print(f"  Watching: {dirs}")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _scan_mtimes(self):
        """Сканировать mtimes всех .py файлов."""
        mtimes = {}
        for watch_dir in self.watch_dirs:
            for root, _dirs, files in os.walk(watch_dir):
                for f in files:
                    if f.endswith(".py"):
                        path = os.path.join(root, f)
                        try:
                            mtimes[path] = os.path.getmtime(path)
                        except OSError:
                            pass
        return mtimes

    def _watch_loop(self):
        """Polling loop (простой, без watchdog dependency)."""
        while self._running:
            time.sleep(0.5)  # poll interval
            new_mtimes = self._scan_mtimes()

            changed = []
            for path, mtime in new_mtimes.items():
                old_mtime = self._file_mtimes.get(path)
                if old_mtime is None or mtime > old_mtime:
                    changed.append(path)

            # Проверить удалённые файлы
            for path in set(self._file_mtimes) - set(new_mtimes):
                changed.append(path)

            self._file_mtimes = new_mtimes

            if changed:
                now = time.time()
                if now - self._last_trigger > self.debounce:
                    self._last_trigger = now
                    rel = [os.path.relpath(p) for p in changed[:5]]
                    print(f"\n  Changed: {', '.join(rel)}")
                    try:
                        self.callback(changed)
                    except Exception as e:
                        print(f"  Rebuild error: {e}")
