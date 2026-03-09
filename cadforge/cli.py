"""
CLI — точка входа cadforge.

Usage:
    cadforge build     — validate + build + export
    cadforge validate  — только статический анализ
    cadforge dev       — dev server с hot reload
    cadforge export    — конвертация STL → glTF
"""
import argparse
import os
import sys
import time
import webbrowser


def cmd_build(args):
    """Полная сборка: validate → build → export."""
    from . import manifest, compiler, exporter

    m = manifest.load(args.root)
    result = compiler.compile_and_build(m)

    if result["success"] and "gltf" in m["export"].get("formats", []):
        print("\n  Phase 3: Converting to glTF...")
        exporter.stl_to_gltf(result["export_dir"], project_root=m["root_dir"])
        if not args.keep_stl:
            exporter.cleanup_stls(result["export_dir"])

    return 0 if result["success"] else 1


def cmd_validate(args):
    """Только статический анализ."""
    from . import manifest, compiler

    m = manifest.load(args.root)
    result = compiler.validate(m)

    if result["valid"]:
        print("  ✓ All modules valid")
    else:
        print("  ✗ Validation failed:")
        for e in result["errors"]:
            print(f"    {e}")

    for w in result["warnings"]:
        print(f"    WARN: {w}")

    return 0 if result["valid"] else 1


def cmd_dev(args):
    """Dev server с hot reload."""
    from . import manifest, compiler, exporter, server, watcher

    m = manifest.load(args.root)
    root = m["root_dir"]
    project_dir = os.path.join(root, m["project"].get("project_dir", "project"))
    dist_dir = os.path.join(root, m["export"].get("output_dir", "dist"))
    os.makedirs(dist_dir, exist_ok=True)

    port = m["dev"].get("port", 3000)
    ws_port = m["dev"].get("ws_port", 3001)

    print("=" * 50)
    print("  CADFORGE DEV SERVER")
    print("=" * 50)

    # Начальная сборка
    print("\n  Initial build...")
    result = compiler.compile_and_build(m)
    if result["success"] and "gltf" in m["export"].get("formats", []):
        exporter.stl_to_gltf(result["export_dir"], project_root=m["root_dir"])
        exporter.cleanup_stls(result["export_dir"])

    # Стартуем серверы
    server.start_http(root, dist_dir, port)

    try:
        server.start_websocket(ws_port)
    except Exception as e:
        print(f"  WARN: WebSocket not available ({e})")
        print("  Install: pip install websockets")

    # File watcher
    def on_change(changed_files):
        server.notify_clients("build_start")
        t0 = time.time()

        result = compiler.compile_and_build(m)
        if result["success"] and "gltf" in m["export"].get("formats", []):
            exporter.stl_to_gltf(result["export_dir"], project_root=m["root_dir"])
            exporter.cleanup_stls(result["export_dir"])

        elapsed = time.time() - t0
        if result["success"]:
            server.notify_clients("build_complete", {
                "time": round(elapsed, 2),
                "objects": len(result.get("objects", [])),
            })
        else:
            server.notify_clients("build_error", {
                "errors": result.get("errors", []),
            })

    w = watcher.ProjectWatcher(
        [project_dir],
        on_change,
        debounce_ms=m["dev"].get("debounce_ms", 500),
    )
    w.start()

    url = f"http://localhost:{port}"
    print(f"\n  → Open: {url}")

    if m["dev"].get("auto_open", True):
        webbrowser.open(url)

    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        w.stop()


def cmd_export(args):
    """Конвертация STL → glTF."""
    from . import manifest, exporter

    m = manifest.load(args.root)
    dist_dir = os.path.join(m["root_dir"], m["export"].get("output_dir", "dist"))
    result = exporter.stl_to_gltf(dist_dir)
    if result:
        print(f"  ✓ Exported: {result}")
    return 0 if result else 1


def main():
    parser = argparse.ArgumentParser(
        prog="cadforge",
        description="CadForge — модульный CAD-фреймворк",
    )
    parser.add_argument(
        "--root", default=os.getcwd(),
        help="Root directory with cadforge.toml",
    )

    sub = parser.add_subparsers(dest="command")

    p_build = sub.add_parser("build", help="Validate + build + export")
    p_build.add_argument("--keep-stl", action="store_true", help="Keep individual STL files")

    sub.add_parser("validate", help="Static analysis only")
    sub.add_parser("dev", help="Dev server with hot reload")
    sub.add_parser("export", help="Convert STL to glTF")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    commands = {
        "build": cmd_build,
        "validate": cmd_validate,
        "dev": cmd_dev,
        "export": cmd_export,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
