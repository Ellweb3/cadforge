"""
Гостевой дом 33 м² — 3x11м, односкатная крыша.
Планировка: санузел 2м, спальня 4м, гостиная+кухня 5м.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj, wcut


def build(doc):
    """Построить гостевой дом целиком."""
    _slab(doc)
    _floors(doc)
    _walls(doc)
    _roof(doc)
    _siding(doc)


def _slab(doc):
    g_slab = Part.makeBox(G_W + 0.2 * M, G_L + 0.2 * M, SLAB_T)
    g_slab.translate(FreeCAD.Vector(GX - 0.1 * M, GY - 0.1 * M, 0))
    add_obj(doc, "G_Slab", g_slab, COL_SLAB)


def _floors(doc):
    floors = [
        ("G_FL_Bath", GX + WALL_T, GY + WALL_T,
         G_W - 2 * WALL_T, G_BATH_L * M - INNER_T, FL_BATH),
        ("G_FL_Bed", GX + WALL_T, GY + G_BATH_L * M + INNER_T,
         G_W - 2 * WALL_T, G_BED_L * M - INNER_T, FL_BEDROOM),
        ("G_FL_Liv", GX + WALL_T, GY + (G_BATH_L + G_BED_L) * M + INNER_T,
         G_W - 2 * WALL_T, G_LIVING_L * M - WALL_T - INNER_T, FL_LIVING),
    ]
    for name, fx, fy, fw, fd, col in floors:
        fl = Part.makeBox(fw, fd, FLOOR_H)
        fl.translate(FreeCAD.Vector(fx, fy, SLAB_T))
        add_obj(doc, name, fl, col)


def _walls(doc):
    """Наружные стены + внутренние перегородки + вырезы."""
    # Коробка стен до G_HL
    outer = Part.makeBox(G_W, G_L, G_HL)
    inner = Part.makeBox(G_W - 2 * WALL_T, G_L - 2 * WALL_T, G_HL + 100)
    inner.translate(FreeCAD.Vector(WALL_T, WALL_T, WALL_T))
    walls = outer.cut(inner)
    walls.translate(FreeCAD.Vector(GX, GY, SLAB_T))

    # Надстройка левой стены (от G_HL до G_HH)
    ext_left = Part.makeBox(WALL_T, G_L, G_HH - G_HL)
    ext_left.translate(FreeCAD.Vector(GX, GY, SLAB_T + G_HL))
    walls = walls.fuse(ext_left)

    # Треугольные фронтоны
    dh = G_HH - G_HL
    for ty in [GY, GY + G_L - WALL_T]:
        p1 = FreeCAD.Vector(0, 0, 0)
        p2 = FreeCAD.Vector(0, 0, dh)
        p3 = FreeCAD.Vector(G_W, 0, 0)
        wire = Part.makePolygon([p1, p2, p3, p1])
        face = Part.Face(wire)
        tri = face.extrude(FreeCAD.Vector(0, WALL_T, 0))
        tri.translate(FreeCAD.Vector(GX, ty, SLAB_T + G_HL))
        walls = walls.fuse(tri)

    # Вырезы окон и двери
    gwt3 = WALL_T * 3
    # Дверь (восток, гостиная)
    walls = walls.cut(wcut(GX + G_W - gwt3 / 2, GY + 8.0 * M, SLAB_T,
                           gwt3, 0.9 * M, 2.2 * M, "x"))
    # Окно гостиной (восток, большое)
    walls = walls.cut(wcut(GX + G_W - gwt3 / 2, GY + 9.5 * M,
                           SLAB_T + 0.9 * M, gwt3, 1.8 * M, 1.4 * M, "x"))
    # Окно спальни (восток)
    walls = walls.cut(wcut(GX + G_W - gwt3 / 2, GY + 3.5 * M,
                           SLAB_T + 0.9 * M, gwt3, 1.2 * M, 1.4 * M, "x"))
    # Окно санузла (восток, маленькое)
    walls = walls.cut(wcut(GX + G_W - gwt3 / 2, GY + 0.7 * M,
                           SLAB_T + 1.5 * M, gwt3, 0.6 * M, 0.6 * M, "x"))
    # Окно северный торец (гостиная)
    walls = walls.cut(wcut(GX + 0.75 * M, GY + G_L - gwt3 / 2,
                           SLAB_T + 0.9 * M, 1.5 * M, 1.4 * M, gwt3))
    # Окно южный торец (санузел)
    walls = walls.cut(wcut(GX + 1.2 * M, GY - gwt3 / 2,
                           SLAB_T + 1.5 * M, 0.6 * M, 0.6 * M, gwt3))

    add_obj(doc, "G_Walls", walls, COL_SIDING)

    # Внутренние стены
    iw1 = Part.makeBox(G_W - 2 * WALL_T, INNER_T, G_HL - 0.1 * M)
    iw1.translate(FreeCAD.Vector(GX + WALL_T, GY + G_BATH_L * M, SLAB_T))
    add_obj(doc, "G_IW1", iw1, COL_WALL_INT)

    iw2 = Part.makeBox(G_W - 2 * WALL_T, INNER_T, G_HL - 0.1 * M)
    iw2.translate(FreeCAD.Vector(GX + WALL_T,
                                 GY + (G_BATH_L + G_BED_L) * M, SLAB_T))
    add_obj(doc, "G_IW2", iw2, COL_WALL_INT)

    # Стёкла окон
    for gy_off, gw_size in [(9.5, 1.8), (3.5, 1.2)]:
        gl = Part.makeBox(25, gw_size * M, 1.4 * M)
        gl.translate(FreeCAD.Vector(GX + G_W - 5, GY + gy_off * M,
                                    SLAB_T + 0.9 * M))
        add_obj(doc, "G_Glass", gl, COL_GLASS, 50)


def _roof(doc):
    """Односкатная крыша."""
    ov = 0.3 * M
    rt = 100
    rp1 = FreeCAD.Vector(-ov, 0, G_HH)
    rp2 = FreeCAD.Vector(G_W + ov, 0, G_HL)
    rp3 = FreeCAD.Vector(G_W + ov, 0, G_HL + rt)
    rp4 = FreeCAD.Vector(-ov, 0, G_HH + rt)
    wire = Part.makePolygon([rp1, rp2, rp3, rp4, rp1])
    face = Part.Face(wire)
    roof = face.extrude(FreeCAD.Vector(0, G_L + 2 * ov, 0))
    roof.translate(FreeCAD.Vector(GX, GY - ov, SLAB_T))
    add_obj(doc, "G_Roof", roof, COL_ROOF)


def _siding(doc):
    """Декоративный сайдинг на фасаде."""
    for i in range(8):
        slat = Part.makeBox(G_W, 15, 20)
        slat.translate(FreeCAD.Vector(GX, GY - 15,
                                      SLAB_T + i * 0.3 * M + 0.15 * M))
        add_obj(doc, "G_Sid_%d" % i, slat, COL_SIDING_DARK)

    # Входная площадка
    entry = Part.makeBox(1.2 * M, 1.2 * M, 40)
    entry.translate(FreeCAD.Vector(GX + G_W, GY + 7.7 * M, 0))
    add_obj(doc, "G_Entry", entry, COL_PATH)
