"""
Общие утилиты для создания объектов FreeCAD.
"""
import FreeCAD
import Part


def add_obj(doc, name, shape, color, transp=0, texture=None, tex_scale=1.0):
    """Добавить объект Part::Feature в документ.

    Args:
        texture: имя файла текстуры из project/textures/ (например "brick.jpg")
        tex_scale: масштаб тайлинга текстуры в метрах (1.0 = 1 повтор на 1м)
    """
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    # Сохраняем цвет как строку в свойстве (работает и headless, и GUI)
    if not hasattr(obj, "CadForgeColor"):
        obj.addProperty("App::PropertyString", "CadForgeColor", "CadForge")
    obj.CadForgeColor = "%s;%s" % (
        ",".join("%.3f" % c for c in color),
        str(transp),
    )
    # Текстура (опционально)
    if texture:
        if not hasattr(obj, "CadForgeTexture"):
            obj.addProperty("App::PropertyString", "CadForgeTexture", "CadForge")
        obj.CadForgeTexture = "%s;%.2f" % (texture, tex_scale)
    # GUI mode — устанавливаем визуальные свойства
    if obj.ViewObject is not None:
        try:
            obj.ViewObject.ShapeColor = color
            obj.ViewObject.Transparency = transp
        except Exception:
            pass
    return obj


def make_box(x, y, z, w, d, h):
    """Создать параллелепипед и сместить."""
    b = Part.makeBox(w, d, h)
    b.translate(FreeCAD.Vector(x, y, z))
    return b


def box_walls(x, y, w, d, h, t, z_base=0):
    """Создать полые стены (коробку) с толщиной t."""
    from .config import SLAB_T
    outer = Part.makeBox(w, d, h)
    inner = Part.makeBox(w - 2*t, d - 2*t, h + 100)
    inner.translate(FreeCAD.Vector(t, t, t))
    result = outer.cut(inner)
    result.translate(FreeCAD.Vector(x, y, z_base + SLAB_T))
    return result


def wcut(x, y, z, w, h, depth, axis="y"):
    """Вырез для окна/двери в стене."""
    if axis == "y":
        b = Part.makeBox(w, depth, h)
    else:
        b = Part.makeBox(depth, w, h)
    b.translate(FreeCAD.Vector(x, y, z))
    return b


def iwall(x1, y1, x2, y2, t, h, z_base=0):
    """Внутренняя стена по двум точкам."""
    from .config import SLAB_T
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if dx >= dy:
        w = Part.makeBox(max(dx, t), t, h)
        w.translate(FreeCAD.Vector(min(x1, x2), min(y1, y2) - t/2, z_base + SLAB_T))
    else:
        w = Part.makeBox(t, max(dy, t), h)
        w.translate(FreeCAD.Vector(min(x1, x2) - t/2, min(y1, y2), z_base + SLAB_T))
    return w
