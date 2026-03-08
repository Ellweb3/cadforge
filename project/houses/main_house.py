"""
Основной дом 88 м² — фундамент, наружные стены, вырезы окон/дверей.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj, box_walls, wcut


def build(doc):
    """Построить фундамент и наружные стены основного дома."""
    _slab(doc)
    _floors(doc)
    walls = _exterior_walls(doc)
    return walls


def _slab(doc):
    """L-образная фундаментная плита."""
    slab_a = Part.makeBox(A_W + 0.2 * M, A_D + 0.2 * M, SLAB_T)
    slab_a.translate(FreeCAD.Vector(AX - 0.1 * M, AY - 0.1 * M, 0))
    slab_b = Part.makeBox(B_W + 0.2 * M, B_D + 0.2 * M, SLAB_T)
    slab_b.translate(FreeCAD.Vector(BX - 0.1 * M, BY - 0.1 * M, 0))
    add_obj(doc, "Slab", slab_a.fuse(slab_b), COL_SLAB)


def _floors(doc):
    """Цветные полы по комнатам."""
    floors = [
        ("FL_Liv", AX + WALL_T, AY + WALL_T,
         A_W - 2 * WALL_T, A_D - 2 * WALL_T, FL_LIVING),
        ("FL_Cor", BX + B_W - WALL_T - CORR_W, BY + WALL_T,
         CORR_W, B_D - 2 * WALL_T - DORM1_H, FL_HALL),
        ("FL_D1", BX + WALL_T, BY + B_D - WALL_T - DORM1_H,
         B_W - 2 * WALL_T, DORM1_H, FL_BEDROOM),
        ("FL_B1", BX + WALL_T,
         BY + B_D - WALL_T - DORM1_H - BANO1_H,
         B_W - 2 * WALL_T - CORR_W, BANO1_H, FL_BATH),
        ("FL_B2", BX + WALL_T,
         BY + B_D - WALL_T - DORM1_H - BANO1_H - BANO2_H,
         B_W - 2 * WALL_T - CORR_W, BANO2_H, FL_BATH),
        ("FL_D2", BX + WALL_T, BY + WALL_T + DORM3_H,
         B_W - 2 * WALL_T - CORR_W, DORM2_H, FL_BEDROOM),
        ("FL_D3", BX + WALL_T, BY + WALL_T,
         B_W - 2 * WALL_T - CORR_W, DORM3_H, FL_BEDROOM),
    ]
    for name, fx, fy, fw, fd, col in floors:
        fl = Part.makeBox(fw, fd, FLOOR_H)
        fl.translate(FreeCAD.Vector(fx, fy, SLAB_T))
        add_obj(doc, name, fl, col)


def _exterior_walls(doc):
    """Наружные стены с вырезами окон и дверей."""
    walls_a = box_walls(AX, AY, A_W, A_D, WALL_H, WALL_T)
    walls_b = box_walls(BX, BY, B_W, B_D, WALL_H, WALL_T)
    w = walls_a.fuse(walls_b)

    wt3 = WALL_T * 3

    # --- Блок A (гостиная) ---
    # Панорамные окна (юг)
    w = w.cut(wcut(AX + 1.5 * M, AY - wt3 / 2, SLAB_T + 0.05 * M,
                   2.20 * M, 2.08 * M, wt3))
    w = w.cut(wcut(AX + 4.2 * M, AY - wt3 / 2, SLAB_T + 0.05 * M,
                   2.20 * M, 2.08 * M, wt3))
    # Дверь-окно
    w = w.cut(wcut(AX + A_W - 4.0 * M, AY - wt3 / 2, SLAB_T,
                   3.30 * M, 2.08 * M, wt3))
    # Окно кухни (восток, наружная стена A)
    w = w.cut(wcut(AX + A_W - wt3 / 2, AY + 1.5 * M, SLAB_T + 0.9 * M,
                   wt3, 1.5 * M, 1.2 * M, "x"))
    # Окно север
    w = w.cut(wcut(AX + 2 * M, AY + A_D - wt3 / 2, SLAB_T + 0.9 * M,
                   1.4 * M, 1.2 * M, wt3))

    # --- Блок B (спальни) ---
    # Окна запад (наружная стена блока B, теперь слева)
    w = w.cut(wcut(BX - wt3 / 2, BY + B_D - 2.5 * M,
                   SLAB_T + 0.5 * M, wt3, 1.4 * M, 1.8 * M, "x"))
    w = w.cut(wcut(BX - wt3 / 2, BY + 3.8 * M,
                   SLAB_T + 0.5 * M, wt3, 1.2 * M, 1.5 * M, "x"))
    w = w.cut(wcut(BX - wt3 / 2, BY + 0.8 * M,
                   SLAB_T + 0.5 * M, wt3, 1.2 * M, 1.5 * M, "x"))
    # Окно юг блок B
    w = w.cut(wcut(BX + 1.0 * M, BY - wt3 / 2, SLAB_T + 0.5 * M,
                   1.0 * M, 1.5 * M, wt3))
    # Маленькие окна санузлов (запад)
    w = w.cut(wcut(BX - wt3 / 2, BY + B_D - 4.5 * M,
                   SLAB_T + 1.2 * M, wt3, 0.6 * M, 0.6 * M, "x"))
    w = w.cut(wcut(BX - wt3 / 2, BY + B_D - 6.5 * M,
                   SLAB_T + 1.2 * M, wt3, 0.6 * M, 0.6 * M, "x"))
    # Входная дверь (восток блока B, стык с A)
    w = w.cut(wcut(BX + B_W - wt3 / 2, BY + 8 * M, SLAB_T,
                   wt3, 1.0 * M, 2.2 * M, "x"))

    add_obj(doc, "Ext_Walls", w, COL_SIDING)
    return w
