"""
Крыши основного дома (двускатная + плоская).
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def build(doc):
    """Построить крыши блоков A и B."""
    _roof_block_b(doc)
    _roof_block_a(doc)


def _roof_block_b(doc):
    """Двускатная крыша спального блока B."""
    ov = ROOF_OVERHANG
    p1 = FreeCAD.Vector(-ov, 0, 0)
    p2 = FreeCAD.Vector(B_W + ov, 0, 0)
    p3 = FreeCAD.Vector(B_W / 2, 0, ROOF_B_HEIGHT)
    wire = Part.makePolygon([p1, p2, p3, p1])
    face = Part.Face(wire)
    roof = face.extrude(FreeCAD.Vector(0, B_D + 2 * ov, 0))
    roof.translate(FreeCAD.Vector(BX, BY - ov, SLAB_T + WALL_H))
    add_obj(doc, "Roof_B", roof, COL_ROOF, texture="roof_tile.png", tex_scale=0.5)


def _roof_block_a(doc):
    """Плоская/односкатная крыша гостиной A."""
    ov = ROOF_OVERHANG
    pts = [
        FreeCAD.Vector(-ov, 0, ROOF_A_HEIGHT),
        FreeCAD.Vector(A_W + ov, 0, ROOF_A_HEIGHT),
        FreeCAD.Vector(A_W + ov, 0, 0),
        FreeCAD.Vector(-ov, 0, 0),
    ]
    wire = Part.makePolygon(pts + [pts[0]])
    face = Part.Face(wire)
    roof = face.extrude(FreeCAD.Vector(0, A_D + 2 * ov, 0))
    roof.translate(FreeCAD.Vector(AX, AY - ov, SLAB_T + WALL_H))
    add_obj(doc, "Roof_A", roof, COL_ROOF, texture="roof_tile.png", tex_scale=0.5)
