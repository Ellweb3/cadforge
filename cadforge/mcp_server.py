"""
CadForge MCP Server — AI пишет модули, фреймворк билдит.
Заменяет working_bridge.py, не нужен сокет к FreeCAD GUI.
"""
import json
import os
import sys

# Для запуска как MCP server
try:
    from mcp.server import Server
    from mcp.server.stdio import run_server
    from mcp import types
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def create_server(root_dir=None):
    """Создать MCP сервер для CadForge."""
    if not HAS_MCP:
        raise ImportError("mcp package not installed. pip install mcp")

    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    server = Server("cadforge")

    from . import manifest, compiler, exporter

    @server.tool()
    async def cadforge_build(
        formats: str = "stl,gltf",
    ) -> str:
        """Собрать проект: validate → build → export. Возвращает статус и список объектов."""
        m = manifest.load(root_dir)
        result = compiler.compile_and_build(m)

        if result["success"] and "gltf" in formats.split(","):
            export_dir = result.get("export_dir")
            if export_dir:
                exporter.stl_to_gltf(export_dir)
                exporter.cleanup_stls(export_dir)

        return json.dumps({
            "success": result["success"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "objects_count": len(result.get("objects", [])),
            "build_time": result.get("build_time"),
        }, indent=2)

    @server.tool()
    async def cadforge_validate() -> str:
        """Статический анализ (AST) всех модулей — быстро, без FreeCAD."""
        m = manifest.load(root_dir)
        result = compiler.validate(m)
        return json.dumps({
            "valid": result["valid"],
            "errors": [str(e) for e in result["errors"]],
            "warnings": result["warnings"],
        }, indent=2)

    @server.tool()
    async def cadforge_read_module(module: str) -> str:
        """Прочитать исходный код модуля. Пример: module='houses.main_house'"""
        m = manifest.load(root_dir)
        project_dir = os.path.join(root_dir, m["project"].get("project_dir", "project"))
        path = os.path.join(project_dir, module.replace(".", "/") + ".py")
        if not os.path.exists(path):
            return json.dumps({"error": f"Module not found: {path}"})
        with open(path, "r") as f:
            return f.read()

    @server.tool()
    async def cadforge_write_module(module: str, code: str) -> str:
        """Записать/обновить модуль проекта. Пример: module='houses.main_house', code='...'"""
        m = manifest.load(root_dir)
        project_dir = os.path.join(root_dir, m["project"].get("project_dir", "project"))
        path = os.path.join(project_dir, module.replace(".", "/") + ".py")

        # Создать директорию если нет
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Проверить синтаксис перед записью
        import ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            return json.dumps({
                "error": f"SyntaxError: {e.msg} at line {e.lineno}",
                "written": False,
            })

        with open(path, "w") as f:
            f.write(code)

        return json.dumps({
            "written": True,
            "path": path,
            "message": f"Module {module} updated. Run cadforge_build to rebuild.",
        })

    @server.tool()
    async def cadforge_read_config() -> str:
        """Прочитать текущие параметры проекта (config.py)."""
        m = manifest.load(root_dir)
        project_dir = os.path.join(root_dir, m["project"].get("project_dir", "project"))
        path = os.path.join(project_dir, "config.py")
        if not os.path.exists(path):
            return json.dumps({"error": "config.py not found"})
        with open(path, "r") as f:
            return f.read()

    @server.tool()
    async def cadforge_list_objects() -> str:
        """Список объектов из последнего билда (имена, цвета, размеры)."""
        m = manifest.load(root_dir)
        dist = os.path.join(root_dir, m["export"].get("output_dir", "dist"))
        manifest_path = os.path.join(dist, "manifest.json")
        if not os.path.exists(manifest_path):
            return json.dumps({"error": "No build yet. Run cadforge_build first."})
        with open(manifest_path, "r") as f:
            objects = json.load(f)
        return json.dumps({
            "count": len(objects),
            "objects": [
                {"name": o["name"], "color": o["color"], "volume": round(o.get("volume", 0), 1)}
                for o in objects
            ]
        }, indent=2)

    @server.tool()
    async def cadforge_list_modules() -> str:
        """Список модулей проекта из cadforge.toml."""
        m = manifest.load(root_dir)
        return json.dumps({
            "project": m["project"]["name"],
            "modules": m["modules"].get("sequence", []),
            "project_dir": m["project"].get("project_dir", "project"),
        }, indent=2)

    return server


async def main():
    """Entry point для MCP server."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server = create_server(root_dir)
    await run_server(server)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
