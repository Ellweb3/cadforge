"""
Сайдинг, дорожки, террасы, входные площадки.
"""
import FreeCAD
import Part
from ..config import *
from ..helpers import add_obj


def build(doc):
    """Добавить отделку и благоустройство."""
    _siding(doc)
    _paths(doc)
    _terrace(doc)


def _siding(doc):
    """Горизонтальный сайдинг на фасадах."""
    # Блок A (южный фасад)
    for i in range(8):
        slat = Part.makeBox(A_W, 15, 20)
        slat.translate(FreeCAD.Vector(
            AX, AY - 15, SLAB_T + i * 0.3 * M + 0.15 * M))
        add_obj(doc, "Sid_A_%d" % i, slat, COL_SIDING_DARK)

    # Блок B (южный торец)
    for i in range(8):
        slat = Part.makeBox(B_W, 15, 20)
        slat.translate(FreeCAD.Vector(
            BX, BY - 15, SLAB_T + i * 0.3 * M + 0.15 * M))
        add_obj(doc, "Sid_B_%d" % i, slat, COL_SIDING_DARK)


def _paths(doc):
    """Дорожки и входные площадки."""
    # Дорожка от забора к дому
    path = Part.makeBox(1.5 * M, HOUSE_Y, 30)
    path.translate(FreeCAD.Vector(BX + B_W - 0.5 * M, 0, 0))
    add_obj(doc, "Path", path, COL_SLAB)

    # Площадка перед входом
    entry = Part.makeBox(3 * M, 2 * M, 40)
    entry.translate(FreeCAD.Vector(BX + B_W - 1.5 * M, AY - 3 * M, 0))
    add_obj(doc, "Entry", entry, COL_PATH)


def _terrace(doc):
    """Деревянная терраса перед гостиной."""
    terrace = Part.makeBox(A_W - 1 * M, 3 * M, 0.12 * M)
    terrace.translate(FreeCAD.Vector(AX + 0.5 * M, AY - 3.5 * M, 0))
    add_obj(doc, "Terrace", terrace, COL_TERRACE)
