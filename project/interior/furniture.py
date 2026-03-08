"""
Мебель и сантехника обоих домов.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def _furn(doc, name, x, y, w, d, col=COL_FURNITURE, h=80):
    f = Part.makeBox(w, d, h)
    f.translate(FreeCAD.Vector(x, y, SLAB_T + FLOOR_H))
    return add_obj(doc, name, f, col)


def _fix(doc, name, x, y, w, d):
    return _furn(doc, name, x, y, w, d, COL_FIXTURE)


def build(doc):
    """Расставить мебель в обоих домах."""
    _main_house(doc)
    _guest_house(doc)


def _main_house(doc):
    """Мебель основного дома 88 м²."""
    # --- Гостиная-Кухня (Блок A) ---
    _furn(doc, "Kitchen_L", AX + WALL_T + 0.1 * M, AY + WALL_T + 0.1 * M,
          0.6 * M, 3.5 * M, COL_COUNTER)
    _furn(doc, "Kitchen_top", AX + WALL_T + 0.1 * M, AY + WALL_T + 0.1 * M,
          2.5 * M, 0.6 * M, COL_COUNTER)
    _furn(doc, "Fridge", AX + WALL_T + 0.1 * M,
          AY + A_D - WALL_T - 0.7 * M, 0.65 * M, 0.6 * M, (0.85, 0.85, 0.87))

    # Обеденный стол + стулья
    _furn(doc, "Table", AX + 3.0 * M, AY + 1.2 * M,
          1.4 * M, 1.0 * M, (0.5, 0.4, 0.3))
    for sx, sy in [(3.1, 0.9), (3.7, 0.9), (4.1, 0.9),
                    (3.1, 2.3), (3.7, 2.3), (4.1, 2.3)]:
        _furn(doc, "Chair", AX + sx * M, AY + sy * M,
              0.4 * M, 0.4 * M, (0.5, 0.45, 0.35))

    # Диван L-образный
    _furn(doc, "Sofa_L", AX + 5.5 * M, AY + WALL_T + 0.3 * M,
          2.5 * M, 0.85 * M, (0.45, 0.45, 0.48))
    _furn(doc, "Sofa_S", AX + 5.5 * M, AY + WALL_T + 0.3 * M,
          0.85 * M, 2.0 * M, (0.45, 0.45, 0.48))
    _furn(doc, "TV", AX + 7.5 * M, AY + WALL_T + 0.3 * M,
          0.05 * M, 1.0 * M, (0.1, 0.1, 0.1))
    _furn(doc, "CoffeeTbl", AX + 6.5 * M, AY + 1.5 * M,
          0.8 * M, 0.5 * M, (0.5, 0.4, 0.3))

    # --- Dormitorio 1 (мастер) ---
    d1x = BX + WALL_T + 0.5 * M
    d1y = BY + B_D - WALL_T - 3.0 * M
    _furn(doc, "Bed1", d1x + 0.3 * M, d1y, 1.6 * M, 2.0 * M, (0.7, 0.65, 0.6))
    _furn(doc, "Night1_L", d1x, d1y + 0.3 * M, 0.4 * M, 0.4 * M)
    _furn(doc, "Night1_R", d1x + 2.2 * M, d1y + 0.3 * M, 0.4 * M, 0.4 * M)

    # --- Dormitorio 2 ---
    d2x = BX + WALL_T + CORR_W + 0.15 * M
    d2y = BY + WALL_T + DORM3_H + 0.15 * M
    _furn(doc, "Bed2", d2x + 0.2 * M, d2y + 0.3 * M,
          1.4 * M, 1.9 * M, (0.7, 0.7, 0.68))
    _furn(doc, "Placard2", d2x + 0.1 * M, d2y + 2.4 * M,
          2.0 * M, 0.5 * M, (0.5, 0.4, 0.35))

    # --- Dormitorio 3 ---
    d3x = BX + WALL_T + CORR_W + 0.15 * M
    d3y = BY + WALL_T + 0.15 * M
    _furn(doc, "Bed3", d3x + 0.2 * M, d3y + 0.3 * M,
          1.4 * M, 1.9 * M, (0.7, 0.7, 0.68))
    _furn(doc, "Placard3", d3x + 0.1 * M, d3y + 2.5 * M,
          2.0 * M, 0.5 * M, (0.5, 0.4, 0.35))

    # --- Bano 1 ---
    b1x = BX + WALL_T + CORR_W + 0.1 * M
    b1y = BY + B_D - WALL_T - DORM1_H - BANO1_H + 0.1 * M
    _fix(doc, "Toilet1", b1x + 1.5 * M, b1y + 0.1 * M, 0.4 * M, 0.6 * M)
    _fix(doc, "Sink1", b1x + 0.5 * M, b1y + 0.1 * M, 0.5 * M, 0.4 * M)
    _fix(doc, "Shower1", b1x + 0.1 * M, b1y + 0.8 * M, 0.9 * M, 0.9 * M)

    # --- Bano 2 ---
    b2x = BX + WALL_T + CORR_W + 0.1 * M
    b2y = BY + B_D - WALL_T - DORM1_H - BANO1_H - BANO2_H + 0.1 * M
    _fix(doc, "Toilet2", b2x + 1.5 * M, b2y + 0.1 * M, 0.4 * M, 0.6 * M)
    _fix(doc, "Sink2", b2x + 0.5 * M, b2y + 0.1 * M, 0.5 * M, 0.4 * M)
    _fix(doc, "Bathtub2", b2x + 0.1 * M, b2y + 0.7 * M, 0.7 * M, 1.0 * M)


def _guest_house(doc):
    """Мебель гостевого дома 33 м²."""
    gfx = GX + WALL_T + 0.1 * M

    # Санузел
    _fix(doc, "G_Toilet", gfx + 1.5 * M, GY + WALL_T + 0.1 * M,
         0.4 * M, 0.6 * M)
    _fix(doc, "G_Sink", gfx + 0.8 * M, GY + WALL_T + 0.1 * M,
         0.5 * M, 0.4 * M)
    _fix(doc, "G_Shower", gfx + 0.1 * M, GY + WALL_T + 0.7 * M,
         0.9 * M, 0.9 * M)

    # Спальня
    _furn(doc, "G_Bed", gfx + 0.3 * M, GY + 2.5 * M,
          1.6 * M, 2.0 * M, (0.7, 0.65, 0.6))
    _furn(doc, "G_Night_L", gfx + 0.1 * M, GY + 2.8 * M,
          0.35 * M, 0.35 * M)
    _furn(doc, "G_Night_R", gfx + 2.1 * M, GY + 2.8 * M,
          0.35 * M, 0.35 * M)
    _furn(doc, "G_Wardrobe", gfx + 0.2 * M, GY + 5.0 * M,
          2.0 * M, 0.5 * M, (0.5, 0.4, 0.35))

    # Гостиная + кухня
    _furn(doc, "G_Kitchen", gfx, GY + 6.3 * M,
          0.6 * M, 2.5 * M, COL_COUNTER)
    _fix(doc, "G_KSink", gfx + 0.05 * M, GY + 7.5 * M, 0.5 * M, 0.5 * M)
    _furn(doc, "G_Fridge", gfx, GY + 9.8 * M,
          0.6 * M, 0.6 * M, (0.85, 0.85, 0.87))
    _furn(doc, "G_Sofa", gfx + 0.8 * M, GY + 9.0 * M,
          1.6 * M, 0.7 * M, (0.45, 0.45, 0.48))
    _furn(doc, "G_Table", gfx + 0.9 * M, GY + 7.5 * M,
          1.0 * M, 0.7 * M, (0.5, 0.4, 0.3))
    _furn(doc, "G_Chair1", gfx + 0.8 * M, GY + 7.0 * M,
          0.4 * M, 0.4 * M, (0.5, 0.45, 0.35))
    _furn(doc, "G_Chair2", gfx + 1.5 * M, GY + 7.0 * M,
          0.4 * M, 0.4 * M, (0.5, 0.45, 0.35))
