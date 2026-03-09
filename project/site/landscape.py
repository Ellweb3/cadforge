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
    _pool(doc)


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

    # --- Живая изгородь вдоль левого забора ---
    for i in range(12):
        hy = 2 * M + i * 3.5 * M
        if hy > FLAT_ZONE - 1 * M:
            break
        hr = random.uniform(0.45 * M, 0.65 * M)
        h = Part.makeSphere(hr)
        h.translate(FreeCAD.Vector(0.7 * M, hy, hr * 0.25))
        sh = random.uniform(-0.02, 0.02)
        add_obj(doc, "Hedge_L_%d" % i, h, (0.22 + sh, 0.50 + sh, 0.18 + sh))

    # --- Живая изгородь вдоль правого забора ---
    for i in range(12):
        hy = 2 * M + i * 3.5 * M
        if hy > FLAT_ZONE - 1 * M:
            break
        hr = random.uniform(0.45 * M, 0.65 * M)
        h = Part.makeSphere(hr)
        h.translate(FreeCAD.Vector(PLOT_W - 0.7 * M, hy, hr * 0.25))
        sh = random.uniform(-0.02, 0.02)
        add_obj(doc, "Hedge_R_%d" % i, h, (0.22 + sh, 0.50 + sh, 0.18 + sh))

    # --- Кусты вдоль переднего забора (дорога) ---
    for i in range(5):
        hx = 2 * M + i * 4 * M
        hr = random.uniform(0.35 * M, 0.5 * M)
        h = Part.makeSphere(hr)
        h.translate(FreeCAD.Vector(hx, 0.7 * M, hr * 0.25))
        add_obj(doc, "Hedge_F_%d" % i, h, (0.28, 0.52, 0.20))

    # --- Цветущие кусты у бассейна ---
    pool_bushes = [
        (POOL_X - 0.8 * M, POOL_Y + 0.5 * M, 0.4 * M),
        (POOL_X - 0.8 * M, POOL_Y + POOL_D - 0.5 * M, 0.35 * M),
        (POOL_X + POOL_W + 0.8 * M, POOL_Y + 0.5 * M, 0.38 * M),
        (POOL_X + POOL_W + 0.8 * M, POOL_Y + POOL_D - 0.5 * M, 0.42 * M),
        (POOL_X + POOL_W / 2, POOL_Y + POOL_D + 1 * M, 0.5 * M),
    ]
    for i, (px, py, pr) in enumerate(pool_bushes):
        fb = Part.makeSphere(pr)
        fb.translate(FreeCAD.Vector(px, py, pr * 0.3))
        add_obj(doc, "FlowerBush_%d" % i, fb, (0.4, 0.55, 0.25))

    # --- Низкие круглые кусты-шарики по саду ---
    garden_balls = [
        (5 * M, 8 * M, 0.3 * M),
        (7 * M, 6 * M, 0.25 * M),
        (17 * M, 8 * M, 0.3 * M),
        (18 * M, 12 * M, 0.28 * M),
        (2 * M, 20 * M, 0.32 * M),
        (20 * M, 25 * M, 0.3 * M),
        (2 * M, 35 * M, 0.35 * M),
        (20 * M, 35 * M, 0.3 * M),
        (10 * M, 42 * M, 0.4 * M),
        (15 * M, 44 * M, 0.35 * M),
        (5 * M, 44 * M, 0.3 * M),
    ]
    for i, (gx, gy, gr) in enumerate(garden_balls):
        gb = Part.makeSphere(gr)
        gb.translate(FreeCAD.Vector(gx, gy, gr * 0.2))
        sh = random.uniform(-0.03, 0.03)
        add_obj(doc, "GardenBall_%d" % i, gb,
                (0.25 + sh, 0.52 + sh, 0.15 + sh))


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


def _pool(doc):
    """Бассейн 6×3 м."""
    t = POOL_WALL_T
    # Чаша — внешний короб минус внутренний
    outer = Part.makeBox(POOL_W, POOL_D, POOL_DEPTH)
    inner = Part.makeBox(POOL_W - 2 * t, POOL_D - 2 * t, POOL_DEPTH + 100)
    inner.translate(FreeCAD.Vector(t, t, t))
    bowl = outer.cut(inner)
    bowl.translate(FreeCAD.Vector(POOL_X, POOL_Y, -POOL_DEPTH))
    add_obj(doc, "Pool_Bowl", bowl, COL_POOL_WALL)

    # Бортик (кромка вокруг бассейна)
    rim = Part.makeBox(POOL_W + 2 * t, POOL_D + 2 * t, 80)
    rim_hole = Part.makeBox(POOL_W, POOL_D, 200)
    rim_hole.translate(FreeCAD.Vector(t, t, -50))
    rim = rim.cut(rim_hole)
    rim.translate(FreeCAD.Vector(POOL_X - t, POOL_Y - t, 0))
    add_obj(doc, "Pool_Rim", rim, COL_POOL_WALL)

    # Вода
    water = Part.makeBox(POOL_W - 2 * t, POOL_D - 2 * t, POOL_DEPTH - 100)
    water.translate(FreeCAD.Vector(POOL_X + t, POOL_Y + t, -POOL_DEPTH + t))
    add_obj(doc, "Pool_Water", water, COL_POOL_WATER, transp=40)
