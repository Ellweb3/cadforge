"""
Участок: земля, овраг, забор.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def build(doc):
    """Создать участок, овраг и забор."""
    # Земля (ровная часть)
    ground = Part.makeBox(PLOT_W, FLAT_ZONE, 80)
    ground.translate(FreeCAD.Vector(0, 0, -80))
    add_obj(doc, "Ground", ground, COL_GROUND)

    # Склон оврага (10 ступеней)
    for i in range(10):
        sd = SLOPE_ZONE / 10
        z = -80 - i * (SLOPE_DROP / 10)
        s = Part.makeBox(PLOT_W, sd + 10, 80 + i * (SLOPE_DROP / 10) + 80)
        s.translate(FreeCAD.Vector(0, FLAT_ZONE + i * sd, z))
        shade = i * 0.005
        add_obj(doc, "Slope_%d" % i, s,
                (COL_SLOPE[0] - shade, COL_SLOPE[1] - shade, COL_SLOPE[2]))

    # Дно оврага
    bottom = Part.makeBox(PLOT_W, SLOPE_ZONE, 100)
    bottom.translate(FreeCAD.Vector(0, FLAT_ZONE, -SLOPE_DROP - 180))
    add_obj(doc, "Ravine", bottom, COL_SWAMP)

    # Забор (4 стороны ровной зоны)
    for nm, x, y, w, d in [
        ("Fence_S", 0, 0, PLOT_W, FENCE_T),
        ("Fence_N", 0, FLAT_ZONE, PLOT_W, FENCE_T),
        ("Fence_W", 0, 0, FENCE_T, FLAT_ZONE),
        ("Fence_E", PLOT_W - FENCE_T, 0, FENCE_T, FLAT_ZONE),
    ]:
        f = Part.makeBox(w, d, FENCE_H)
        f.translate(FreeCAD.Vector(x, y, 0))
        add_obj(doc, nm, f, COL_FENCE)
