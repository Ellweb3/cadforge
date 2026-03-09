# CadForge Project Context

This is a modular CAD project built on FreeCAD. When the user asks to modify the building/site, edit the Python source files — the file watcher will auto-rebuild.

## Key Files

- `project/config.py` — ALL dimensions, positions, colors. Change coordinates here to move/resize things.
- `project/houses/main_house.py` — Main 88m² L-shaped house (Block A = living, Block B = bedrooms)
- `project/houses/guest_house.py` — Guest house 33m²
- `project/site/ground.py` — Ground, ravine, fence
- `project/site/landscape.py` — Trees, bushes
- `project/interior/walls.py` — Interior partition walls
- `project/interior/furniture.py` — Furniture
- `project/exterior/roofs.py` — Roofs
- `project/exterior/windows.py` — Window frames and glass
- `project/exterior/finishing.py` — Siding, paths, terrace
- `project/textures/` — Texture images (brick.png, wood.png, etc.)

## Units

Everything is in millimeters. Use `M = 1000` constant for meters: `5 * M` = 5 meters.

## How add_obj works

```python
add_obj(doc, "Name", shape, (r, g, b), transp=0, texture="brick.png", tex_scale=1.0)
```

## Important

- After editing .py files, the file watcher auto-rebuilds. No manual step needed.
- Keep responses short — the user sees results in the 3D viewer.
- The coordinate system: X = left-right, Y = front(road)-back, Z = up.
- HOUSE_X, HOUSE_Y in config.py control main house position.
