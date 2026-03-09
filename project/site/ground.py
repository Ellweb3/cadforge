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
    add_obj(doc, "Ground", ground, COL_GROUND, texture="grass.png", tex_scale=3.0)

    # Склон оврага (10 ступеней, спуск от уровня земли вниз)
    steps = 10
    sd = SLOPE_ZONE / steps
    drop_step = SLOPE_DROP / steps
    for i in range(steps):
        step_top = -i * drop_step        # верх ступени опускается
        step_h = 80 + drop_step          # толщина ступени
        s = Part.makeBox(PLOT_W, sd + 10, step_h)
        s.translate(FreeCAD.Vector(0, FLAT_ZONE + i * sd, step_top - step_h))
        shade = i * 0.005
        add_obj(doc, "Slope_%d" % i, s,
                (COL_SLOPE[0] - shade, COL_SLOPE[1] - shade, COL_SLOPE[2]))

    # Дно оврага
    bottom = Part.makeBox(PLOT_W, SLOPE_ZONE, 100)
    bottom.translate(FreeCAD.Vector(0, FLAT_ZONE, -SLOPE_DROP - 100))
    add_obj(doc, "Ravine", bottom, COL_SWAMP)

    # Забор — только столбы по периметру
    post_w = 60
    post_spacing = 2.5 * M

    # Передний (Y=0) и задний (за оврагом)
    for nm, y0, z0 in [("FnS", 0, 0), ("FnB", PLOT_D, -SLOPE_DROP)]:
        n = int(PLOT_W / post_spacing) + 1
        for p in range(n):
            post = Part.makeBox(post_w, post_w, FENCE_H)
            post.translate(FreeCAD.Vector(p * post_spacing, y0, z0))
            add_obj(doc, "%s_%d" % (nm, p), post, COL_FENCE)

    # Боковые — ровная часть + спуск по оврагу
    for nm, x in [("FnW", 0), ("FnE", PLOT_W - post_w)]:
        # Ровная часть
        n = int(FLAT_ZONE / post_spacing) + 1
        for p in range(n):
            post = Part.makeBox(post_w, post_w, FENCE_H)
            post.translate(FreeCAD.Vector(x, p * post_spacing, 0))
            add_obj(doc, "%s_%d" % (nm, p), post, COL_FENCE)
        # Спуск по оврагу
        for i in range(steps):
            sy = FLAT_ZONE + i * sd
            sz = -i * drop_step
            post = Part.makeBox(post_w, post_w, FENCE_H)
            post.translate(FreeCAD.Vector(x, sy, sz))
            add_obj(doc, "%s_S%d" % (nm, i), post, COL_FENCE)
