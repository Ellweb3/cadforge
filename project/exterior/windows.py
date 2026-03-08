"""
Остекление и рамы панорамных окон основного дома.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def build(doc):
    """Добавить стёкла и рамы."""
    gt = 25  # толщина стекла

    # Панорамные окна гостиной (фасад юг)
    for wx in [AX + 1.5 * M, AX + 4.2 * M]:
        g = Part.makeBox(2.20 * M, gt, 2.08 * M)
        g.translate(FreeCAD.Vector(wx, AY + WALL_T / 2, SLAB_T + 0.05 * M))
        add_obj(doc, "Glass_PV", g, COL_GLASS, 50)

        # Рамы (3 секции)
        for fx in [0, 0.72 * M, 1.44 * M]:
            frame = Part.makeBox(30, gt + 10, 2.08 * M)
            frame.translate(FreeCAD.Vector(
                wx + fx, AY + WALL_T / 2 - 5, SLAB_T + 0.05 * M))
            add_obj(doc, "Frame", frame, COL_FRAME)

    # Дверь-окно PATENTE
    g = Part.makeBox(3.30 * M, gt, 2.08 * M)
    g.translate(FreeCAD.Vector(
        AX + A_W - 4.0 * M, AY + WALL_T / 2, SLAB_T))
    add_obj(doc, "Glass_Door", g, COL_GLASS, 40)
