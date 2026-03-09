"""
Экспортёр — конвертация STL в glTF/GLB для three.js.
Использует trimesh (вне FreeCAD).
Поддерживает текстуры через box UV projection.
"""
import json
import os


def _box_uv(mesh, scale_mm=1000.0):
    """Генерировать UV-координаты через box projection.

    Для каждого треугольника выбирается проекция по доминирующей оси нормали.
    scale_mm: размер одного тайла текстуры в мм (1000 = 1 повтор на 1 метр).
    """
    import numpy as np

    vertices = mesh.vertices
    faces = mesh.faces
    normals = mesh.face_normals

    uv = np.zeros((len(vertices), 2), dtype=np.float64)
    count = np.zeros(len(vertices), dtype=np.int32)

    for i, (face, normal) in enumerate(zip(faces, normals)):
        abs_n = np.abs(normal)
        axis = np.argmax(abs_n)

        for vi in face:
            v = vertices[vi]
            if axis == 0:  # YZ projection (wall facing X)
                u, vv = v[1] / scale_mm, v[2] / scale_mm
            elif axis == 1:  # XZ projection (wall facing Y)
                u, vv = v[0] / scale_mm, v[2] / scale_mm
            else:  # XY projection (floor/roof facing Z)
                u, vv = v[0] / scale_mm, v[1] / scale_mm

            uv[vi] += [u, vv]
            count[vi] += 1

    # Average UV for shared vertices
    mask = count > 0
    uv[mask] /= count[mask, np.newaxis]

    return uv


def _load_texture_image(texture_name, project_root):
    """Найти и загрузить текстуру из project/textures/."""
    import numpy as np

    search_dirs = [
        os.path.join(project_root, "project", "textures"),
        os.path.join(project_root, "textures"),
    ]

    for d in search_dirs:
        path = os.path.join(d, texture_name)
        if os.path.exists(path):
            try:
                from PIL import Image
                img = Image.open(path).convert("RGBA")
                return np.array(img)
            except ImportError:
                # Fallback: try trimesh's image loading
                import trimesh
                img = trimesh.visual.texture.TextureVisuals._load_image
                # If PIL not available, skip texture
                print(f"  WARN: PIL not installed, skipping texture {texture_name}")
                return None

    print(f"  WARN: texture '{texture_name}' not found in {search_dirs}")
    return None


def stl_to_gltf(export_dir, manifest_path=None, project_root=None):
    """Собрать отдельные STL-файлы в один GLB с цветами и текстурами.

    Args:
        export_dir: директория с STL-файлами и manifest.json
        manifest_path: путь к manifest.json (default: export_dir/manifest.json)
        project_root: корень проекта (для поиска текстур)

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

    if project_root is None:
        project_root = os.path.dirname(export_dir)

    with open(manifest_path, "r") as f:
        objects = json.load(f)

    # Cache loaded texture images
    texture_cache = {}
    scene = trimesh.Scene()

    for obj in objects:
        stl_path = os.path.join(export_dir, obj["stl"])
        if not os.path.exists(stl_path):
            continue

        try:
            mesh = trimesh.load(stl_path)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(mesh.dump())

            texture_name = obj.get("texture")
            tex_scale = obj.get("tex_scale", 1.0)

            if texture_name:
                # Textured material
                if texture_name not in texture_cache:
                    texture_cache[texture_name] = _load_texture_image(
                        texture_name, project_root
                    )

                tex_image = texture_cache[texture_name]
                if tex_image is not None:
                    from PIL import Image as PILImage

                    # Generate UV coordinates
                    scale_mm = tex_scale * 1000.0  # convert m to mm
                    uv = _box_uv(mesh, scale_mm)

                    pil_img = PILImage.fromarray(tex_image)
                    material = trimesh.visual.material.PBRMaterial(
                        baseColorTexture=pil_img,
                        metallicFactor=0.0,
                        roughnessFactor=0.9,
                    )
                    mesh.visual = trimesh.visual.TextureVisuals(
                        uv=uv, material=material
                    )
                else:
                    # Fallback to color
                    _apply_color(mesh, obj, trimesh)
            else:
                # Solid color material
                _apply_color(mesh, obj, trimesh)

            group = obj.get("group", "other").replace(".", "-")
            scene.add_geometry(mesh, node_name=f'{group}--{obj["name"]}')
        except Exception as e:
            print(f"  WARN: skip {obj['name']}: {e}")

    glb_path = os.path.join(export_dir, "model.glb")
    scene.export(glb_path)
    print(f"  Exported glTF: {glb_path} ({os.path.getsize(glb_path) / 1024:.0f} KB)")
    return glb_path


def _apply_color(mesh, obj, trimesh):
    """Применить PBR-материал со сплошным цветом."""
    color = obj.get("color", [0.7, 0.7, 0.7])
    alpha = 1.0 - obj.get("transparency", 0) / 100.0
    rgba = [int(c * 255) for c in color] + [int(alpha * 255)]

    material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=rgba,
        metallicFactor=0.1,
        roughnessFactor=0.8,
    )
    mesh.visual = trimesh.visual.TextureVisuals(material=material)


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
