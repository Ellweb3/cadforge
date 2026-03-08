"""
Главный скрипт сборки проекта.
Запуск: FreeCAD -> Macro -> Execute Macro -> build.py

Собирает весь проект из модулей в правильном порядке.
"""
import sys
import os

# Добавляем parent в path чтобы работали импорты project.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import FreeCAD
from project.site import ground, landscape
from project.houses import main_house, guest_house
from project.interior import walls, furniture
from project.exterior import roofs, windows, finishing

# Используем активный документ или создаём новый
doc = FreeCAD.ActiveDocument
if doc is None:
    doc = FreeCAD.newDocument("House_88m2")
else:
    for obj in doc.Objects:
        doc.removeObject(obj.Name)

print("=" * 50)
print("  BUILDING PROJECT...")
print("=" * 50)

# 1. Участок
print("  [1/7] Site: ground, ravine, fence...")
ground.build(doc)

# 2. Ландшафт
print("  [2/7] Landscape: trees, bushes...")
landscape.build(doc)

# 3. Основной дом — фундамент, стены, окна
print("  [3/7] Main house: slab, walls, openings...")
main_house.build(doc)

# 4. Гостевой дом
print("  [4/7] Guest house: walls, roof...")
guest_house.build(doc)

# 5. Внутренние стены
print("  [5/7] Interior walls...")
walls.build(doc)

# 6. Мебель
print("  [6/7] Furniture...")
furniture.build(doc)

# 7. Экстерьер — крыши, остекление, отделка
print("  [7/7] Exterior: roofs, glass, finishing...")
roofs.build(doc)
windows.build(doc)
finishing.build(doc)

# Финализация
doc.recompute()

try:
    gui = FreeCAD.Gui
    if hasattr(gui, 'ActiveDocument') and gui.ActiveDocument:
        gui.ActiveDocument.ActiveView.viewIsometric()
        gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

print("=" * 50)
print("  PROJECT BUILT SUCCESSFULLY!")
print("  Objects: %d" % len(doc.Objects))
print("=" * 50)
