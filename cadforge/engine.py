"""
Headless FreeCAD engine — запускает FreeCADCmd как subprocess.
Полностью обходит проблему крашей GUI-потока.
"""
import os
import subprocess
import sys
import tempfile
import json


FREECAD_DEFAULT = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"


def find_freecad(manifest=None):
    """Найти путь к freecadcmd."""
    if manifest and manifest.get("project", {}).get("freecad"):
        return manifest["project"]["freecad"]
    if os.path.exists(FREECAD_DEFAULT):
        return FREECAD_DEFAULT
    # Попробовать через PATH
    from shutil import which
    found = which("freecadcmd") or which("FreeCADCmd")
    if found:
        return found
    raise FileNotFoundError(
        "freecadcmd not found. Set 'freecad' in cadforge.toml [project]"
    )


def run_script(script_code, freecad_path=None, timeout=120):
    """Выполнить Python-скрипт в FreeCADCmd headless.

    Returns:
        dict with keys: success, stdout, stderr, returncode
    """
    if freecad_path is None:
        freecad_path = find_freecad()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, prefix="cadforge_"
    ) as f:
        f.write(script_code)
        script_path = f.name

    try:
        result = subprocess.run(
            [freecad_path, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Build timed out after {timeout}s",
            "returncode": -1,
        }
    finally:
        os.unlink(script_path)


def build_project(manifest, export_dir=None):
    """Собрать проект по манифесту и экспортировать геометрию.

    Returns:
        dict: build result with stats, errors, exported files
    """
    root = manifest["root_dir"]
    project_dir = manifest["project"].get("project_dir", "project")
    modules = manifest["modules"].get("sequence", [])
    deflection = manifest["export"].get("mesh_deflection", 0.5)

    if export_dir is None:
        export_dir = os.path.join(root, manifest["export"].get("output_dir", "dist"))
    os.makedirs(export_dir, exist_ok=True)

    project_abs = os.path.join(root, project_dir)
    manifest_json = os.path.join(export_dir, "manifest.json")

    script = _generate_build_script(
        root_dir=root,
        project_abs=project_abs,
        modules=modules,
        export_dir=export_dir,
        manifest_json=manifest_json,
        deflection=deflection,
    )

    freecad = find_freecad(manifest)
    result = run_script(script, freecad)

    # Собрать результат
    build_result = {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "export_dir": export_dir,
        "objects": [],
    }

    if os.path.exists(manifest_json):
        with open(manifest_json, "r") as f:
            build_result["objects"] = json.load(f)

    return build_result


def _generate_build_script(root_dir, project_abs, modules, export_dir, manifest_json, deflection):
    """Сгенерировать Python-скрипт для FreeCADCmd."""
    module_imports = []
    module_calls = []
    for i, mod in enumerate(modules):
        alias = mod.replace(".", "_")
        module_imports.append(f"from project.{mod} import build as build_{alias}")
        module_calls.append(
            f'_before = set(o.Name for o in doc.Objects)\n'
            f'print("  [{i+1}/{len(modules)}] {mod}...")\n'
            f'build_{alias}(doc)\n'
            f'for _n in set(o.Name for o in doc.Objects) - _before:\n'
            f'    _obj_module[_n] = "{mod}"'
        )

    return f'''\
import sys
import os
import json
import time

# Добавляем корень проекта в path
sys.path.insert(0, {root_dir!r})

import FreeCAD
import MeshPart

# Импорты модулей
{chr(10).join(module_imports)}

print("=" * 50)
print("  CADFORGE BUILD")
print("=" * 50)

doc = FreeCAD.newDocument("CadForge_Build")
t0 = time.time()
_obj_module = {{}}

# Сборка модулей
{chr(10).join(module_calls)}

doc.recompute()

elapsed = time.time() - t0
print(f"  Build time: {{elapsed:.2f}}s")
print(f"  Objects: {{len(doc.Objects)}}")

# Экспорт каждого объекта как STL + манифест с цветами
export_dir = {export_dir!r}
manifest_path = {manifest_json!r}
deflection = {deflection}

objects_meta = []
combined_stl_path = os.path.join(export_dir, "model.stl")
stl_files = []

for obj in doc.Objects:
    if not hasattr(obj, "Shape") or obj.Shape.isNull():
        continue

    name = obj.Name
    stl_path = os.path.join(export_dir, f"{{name}}.stl")

    try:
        mesh = MeshPart.meshFromShape(
            Shape=obj.Shape,
            LinearDeflection=deflection,
            AngularDeflection=0.5,
            Relative=False,
        )
        mesh.write(stl_path)
        stl_files.append(stl_path)

        # Метаданные — читаем цвет из CadForgeColor property
        bb = obj.Shape.BoundBox
        color = [0.7, 0.7, 0.7]
        transp = 0
        if hasattr(obj, "CadForgeColor") and obj.CadForgeColor:
            try:
                parts = obj.CadForgeColor.split(";")
                color = [float(c) for c in parts[0].split(",")]
                if len(parts) > 1:
                    transp = int(parts[1])
            except Exception:
                pass

        meta = {{
            "name": name,
            "stl": f"{{name}}.stl",
            "color": list(color),
            "transparency": transp,
            "bbox": [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax],
            "volume": obj.Shape.Volume,
            "group": _obj_module.get(name, "other"),
        }}
        # Текстура
        if hasattr(obj, "CadForgeTexture") and obj.CadForgeTexture:
            try:
                tex_parts = obj.CadForgeTexture.split(";")
                meta["texture"] = tex_parts[0]
                if len(tex_parts) > 1:
                    meta["tex_scale"] = float(tex_parts[1])
            except Exception:
                pass
        objects_meta.append(meta)
    except Exception as e:
        print(f"  WARN: skip {{name}}: {{e}}")

with open(manifest_path, "w") as f:
    json.dump(objects_meta, f, indent=2)

print(f"  Exported {{len(objects_meta)}} objects to STL")
print("=" * 50)
print("  BUILD COMPLETE")
print("=" * 50)
'''
