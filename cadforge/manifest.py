"""Чтение и валидация cadforge.toml."""
import os

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def load(root_dir=None):
    """Загрузить манифест проекта."""
    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    toml_path = os.path.join(root_dir, "cadforge.toml")
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"cadforge.toml not found in {root_dir}")
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    # Defaults
    proj = data.get("project", {})
    proj.setdefault("units", "mm")
    proj.setdefault("project_dir", "project")

    export = data.get("export", {})
    export.setdefault("formats", ["stl"])
    export.setdefault("mesh_deflection", 0.5)
    export.setdefault("output_dir", "dist")

    dev = data.get("dev", {})
    dev.setdefault("port", 3000)
    dev.setdefault("ws_port", 3001)
    dev.setdefault("watch", ["project/**/*.py"])
    dev.setdefault("auto_open", True)
    dev.setdefault("debounce_ms", 500)

    return {
        "root_dir": root_dir,
        "project": proj,
        "modules": data.get("modules", {}),
        "export": export,
        "dev": dev,
    }
