"""
Экспортёр — конвертация STL в glTF/GLB для three.js.
Использует trimesh (вне FreeCAD).
"""
import json
import os


def stl_to_gltf(export_dir, manifest_path=None):
    """Собрать отдельные STL-файлы в один GLB с цветами.

    Args:
        export_dir: директория с STL-файлами и manifest.json
        manifest_path: путь к manifest.json (default: export_dir/manifest.json)

    Returns:
        str: путь к model.glb
    """
    try:
        import trimesh
        import numpy as np
    except ImportError:
        print("  WARN: trimesh not installed, skipping glTF export")
        print("  Install: pip install trimesh numpy")
        return None

    if manifest_path is None:
        manifest_path = os.path.join(export_dir, "manifest.json")

    if not os.path.exists(manifest_path):
        print("  WARN: manifest.json not found, skipping glTF export")
        return None

    with open(manifest_path, "r") as f:
        objects = json.load(f)

    scene = trimesh.Scene()

    for obj in objects:
        stl_path = os.path.join(export_dir, obj["stl"])
        if not os.path.exists(stl_path):
            continue

        try:
            mesh = trimesh.load(stl_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(mesh.dump())

            # Применить цвет через PBR material (не требует scipy)
            color = obj.get("color", [0.7, 0.7, 0.7])
            alpha = 1.0 - obj.get("transparency", 0) / 100.0
            rgba = [int(c * 255) for c in color] + [int(alpha * 255)]

            material = trimesh.visual.material.PBRMaterial(
                baseColorFactor=rgba,
                metallicFactor=0.1,
                roughnessFactor=0.8,
            )
            mesh.visual = trimesh.visual.TextureVisuals(material=material)

            group = obj.get("group", "other")
            scene.add_geometry(mesh, node_name=f'{group}::{obj["name"]}')
        except Exception as e:
            print(f"  WARN: skip {obj['name']}: {e}")

    glb_path = os.path.join(export_dir, "model.glb")
    scene.export(glb_path)
    print(f"  Exported glTF: {glb_path} ({os.path.getsize(glb_path) / 1024:.0f} KB)")
    return glb_path


def cleanup_stls(export_dir, keep_combined=False):
    """Удалить отдельные STL-файлы после конвертации."""
    manifest_path = os.path.join(export_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return

    with open(manifest_path, "r") as f:
        objects = json.load(f)

    for obj in objects:
        stl_path = os.path.join(export_dir, obj["stl"])
        if os.path.exists(stl_path):
            os.unlink(stl_path)
