"""
Ландшафт: болотная растительность, эвкалипт, кусты, деревья.
"""
import FreeCAD
import Part
import random
from ..config import *
from ..helpers import add_obj

random.seed(42)


def build(doc):
    """Создать всю растительность."""
    _swamp_vegetation(doc)
    _eucalyptus(doc)
    _garden_bushes(doc)
    _garden_trees(doc)


def _swamp_vegetation(doc):
    """Болотные кусты и камыши в овраге."""
    for i in range(18):
        bx = random.uniform(1 * M, 21 * M)
        by = random.uniform(FLAT_ZONE + 1 * M, PLOT_D - 0.5 * M)
        br = random.uniform(0.3 * M, 0.7 * M)
        frac = (by - FLAT_ZONE) / SLOPE_ZONE
        bush = Part.makeSphere(br)
        bush.translate(FreeCAD.Vector(bx, by, -frac * SLOPE_DROP))
        sh = random.uniform(-0.04, 0.04)
        add_obj(doc, "SwBush_%d" % i, bush,
                (COL_BUSH[0] + sh, COL_BUSH[1] + sh, COL_BUSH[2] + sh))

    for i in range(10):
        rx = random.uniform(1 * M, 21 * M)
        ry = random.uniform(FLAT_ZONE + 1.5 * M, PLOT_D - 1 * M)
        frac = (ry - FLAT_ZONE) / SLOPE_ZONE
        reed = Part.makeCylinder(25, random.uniform(1.2 * M, 2 * M))
        reed.translate(FreeCAD.Vector(rx, ry, -frac * SLOPE_DROP))
        add_obj(doc, "Reed_%d" % i, reed, (0.3, 0.5, 0.15))


def _eucalyptus(doc):
    """Эвкалипт в левом дальнем углу."""
    trunk = Part.makeCylinder(0.15 * M, 6 * M)
    trunk.translate(FreeCAD.Vector(EUC_X, EUC_Y, 0))
    add_obj(doc, "Euc_Trunk", trunk, COL_TRUNK)

    for dx, dy, dz, r in [
        (0, 0, 0.5 * M, 1.8 * M),
        (-0.5 * M, 0.3 * M, -0.3 * M, 1.4 * M),
        (0.6 * M, -0.2 * M, 0, 1.3 * M),
        (0, 0.5 * M, 0.3 * M, 1.2 * M),
    ]:
        cr = Part.makeSphere(r)
        cr.translate(FreeCAD.Vector(EUC_X + dx, EUC_Y + dy, 6 * M + dz))
        add_obj(doc, "Euc_Crown", cr, COL_CROWN)


def _garden_bushes(doc):
    """Декоративные кусты вокруг домов."""
    positions = [
        (AX - 1 * M, AY + 1 * M, 0.5 * M),
        (AX - 0.8 * M, AY + 3 * M, 0.4 * M),
        (BX + B_W + 0.8 * M, BY + 2 * M, 0.5 * M),
        (BX + B_W + 0.8 * M, BY + 5 * M, 0.4 * M),
        (BX + B_W + 0.8 * M, BY + 8 * M, 0.5 * M),
        (BX + B_W + 0.8 * M, BY + 11 * M, 0.45 * M),
        (AX + 2 * M, AY - 5 * M, 0.6 * M),
        (AX + 5 * M, AY - 5.5 * M, 0.5 * M),
        (AX + 8 * M, AY - 4.5 * M, 0.45 * M),
    ]
    for i, (bx, by, br) in enumerate(positions):
        b = Part.makeSphere(br)
        b.translate(FreeCAD.Vector(bx, by, br * 0.3))
        add_obj(doc, "GBush_%d" % i, b, (0.3, 0.55, 0.2))


def _garden_trees(doc):
    """Деревья на участке."""
    for i, (tx, ty) in enumerate([
        (3 * M, 15 * M), (19 * M, 18 * M),
        (19 * M, 38 * M), (3 * M, 38 * M),
    ]):
        t = Part.makeCylinder(0.1 * M, 7 * M)
        t.translate(FreeCAD.Vector(tx, ty, 0))
        add_obj(doc, "Tree_t_%d" % i, t, COL_TRUNK)
        cone = Part.makeCone(1.2 * M, 0.1 * M, 5 * M)
        cone.translate(FreeCAD.Vector(tx, ty, 3 * M))
        add_obj(doc, "Tree_c_%d" % i, cone, (0.2, 0.48, 0.18))
