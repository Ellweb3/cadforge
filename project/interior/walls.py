"""
Внутренние стены основного дома.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj, iwall


def build(doc):
    """Создать внутренние перегородки блока B."""
    bi = BX + WALL_T
    br = BX + B_W - WALL_T
    bt = BY + WALL_T
    corr_x = BX + WALL_T + CORR_W
    dorm1_y = BY + B_D - WALL_T - DORM1_H
    bano1_y = dorm1_y - BANO1_H
    bano2_y = bano1_y - BANO2_H
    dorm23_y = bt + DORM3_H

    h = WALL_H - 0.1 * M

    walls = [
        # Стена коридора (вертикальная)
        iwall(corr_x, bt, corr_x, dorm1_y, INNER_T, h),
        # Dorm1 / Bano1
        iwall(bi, dorm1_y, br, dorm1_y, INNER_T, h),
        # Bano1 / Bano2
        iwall(corr_x, bano1_y, br, bano1_y, INNER_T, h),
        # Bano2 / Dorm2
        iwall(corr_x, bano2_y, br, bano2_y, INNER_T, h),
        # Dorm2 / Dorm3
        iwall(corr_x, dorm23_y, br, dorm23_y, INNER_T, h),
    ]

    for i, w in enumerate(walls):
        add_obj(doc, "IW_%d" % i, w, COL_WALL_INT)
