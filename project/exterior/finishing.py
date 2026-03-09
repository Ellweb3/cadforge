"""
Сайдинг, дорожки, террасы, входные площадки.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def build(doc):
    """Добавить отделку и благоустройство."""
    _siding(doc)
    _paths(doc)
    _terrace(doc)


def _siding(doc):
    """Горизонтальный сайдинг на фасадах."""
    # Блок A (южный фасад)
    for i in range(8):
        slat = Part.makeBox(A_W, 15, 20)
        slat.translate(FreeCAD.Vector(
            AX, AY - 15, SLAB_T + i * 0.3 * M + 0.15 * M))
        add_obj(doc, "Sid_A_%d" % i, slat, COL_SIDING_DARK)

    # Блок B (южный торец)
    for i in range(8):
        slat = Part.makeBox(B_W, 15, 20)
        slat.translate(FreeCAD.Vector(
            BX, BY - 15, SLAB_T + i * 0.3 * M + 0.15 * M))
        add_obj(doc, "Sid_B_%d" % i, slat, COL_SIDING_DARK)


def _paths(doc):
    """Изогнутые дорожки и полукруглая входная площадка."""
    path_h = 30   # толщина покрытия
    path_w = 1.2 * M  # ширина дорожки

    # Центр входа — на стыке блоков A и B
    entry_x = AX

    # --- 1. Полукруглая входная площадка ---
    r_entry = 2.0 * M
    center = FreeCAD.Vector(entry_x, AY, 0)
    # Дуга вниз (к дороге): 180° → 360°
    arc = Part.makeCircle(
        r_entry, center, FreeCAD.Vector(0, 0, 1), 180, 360)
    line_close = Part.makeLine(
        FreeCAD.Vector(entry_x + r_entry, AY, 0),
        FreeCAD.Vector(entry_x - r_entry, AY, 0))
    wire_entry = Part.Wire([arc, line_close])
    face_entry = Part.Face(wire_entry)
    entry = face_entry.extrude(FreeCAD.Vector(0, 0, 40))
    add_obj(doc, "Entry_Semi", entry, COL_PATH,
            texture="concrete.png", tex_scale=1.0)

    # --- 2. Главная дорожка: S-кривая от забора до площадки ---
    bottom_y = AY - r_entry  # нижняя точка полукруга
    pts_main = [
        FreeCAD.Vector(entry_x + 2 * M, 0, 0),
        FreeCAD.Vector(entry_x + 3 * M, 7 * M, 0),
        FreeCAD.Vector(entry_x, 14 * M, 0),
        FreeCAD.Vector(entry_x + 1.5 * M, 21 * M, 0),
        FreeCAD.Vector(entry_x, bottom_y, 0),
    ]
    spl = Part.BSplineCurve()
    spl.interpolate(pts_main)
    wire_main = Part.Wire(spl.toShape())
    outline = wire_main.makeOffset2D(path_w / 2)
    face_main = Part.Face(outline)
    main_path = face_main.extrude(FreeCAD.Vector(0, 0, path_h))
    add_obj(doc, "Path_Main", main_path, COL_SLAB,
            texture="concrete.png", tex_scale=1.0)

    # --- 3. Дорожка к бассейну: плавная дуга ---
    mid_y = (AY + A_D + POOL_Y) / 2
    pts_pool = [
        FreeCAD.Vector(AX + A_W / 2, AY + A_D + 0.3 * M, 0),
        FreeCAD.Vector(AX + A_W / 2 + 2.5 * M, mid_y, 0),
        FreeCAD.Vector(POOL_X + POOL_W / 2 + 1 * M, mid_y + 1 * M, 0),
        FreeCAD.Vector(POOL_X + POOL_W / 2, POOL_Y - 0.3 * M, 0),
    ]
    spl2 = Part.BSplineCurve()
    spl2.interpolate(pts_pool)
    wire_pool = Part.Wire(spl2.toShape())
    outline2 = wire_pool.makeOffset2D(0.5 * M)
    face_pool = Part.Face(outline2)
    pool_path = face_pool.extrude(FreeCAD.Vector(0, 0, path_h))
    add_obj(doc, "Path_Pool", pool_path, COL_SLAB,
            texture="concrete.png", tex_scale=1.0)


def _terrace(doc):
    """Деревянная терраса перед гостиной."""
    terrace = Part.makeBox(A_W - 1 * M, 3 * M, 0.12 * M)
    terrace.translate(FreeCAD.Vector(AX + 0.5 * M, AY - 3.5 * M, 0))
    add_obj(doc, "Terrace", terrace, COL_TERRACE, texture="wood.png", tex_scale=1.5)
