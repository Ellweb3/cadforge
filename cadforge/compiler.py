"""
Компилятор — валидация модулей перед сборкой.

Phase 1: Статический анализ (AST) — быстро, без FreeCAD
Phase 2: Сборка через engine (FreeCADCmd headless)
Phase 3: Экспорт геометрии
"""
import ast
import os
import time


class CompileError:
    def __init__(self, module, message, line=None):
        self.module = module
        self.message = message
        self.line = line

    def __str__(self):
        loc = f":{self.line}" if self.line else ""
        return f"[{self.module}{loc}] {self.message}"


def validate(manifest):
    """Phase 1: статическая валидация всех модулей.

    Returns:
        dict: {valid: bool, errors: list[CompileError], warnings: list[str]}
    """
    root = manifest["root_dir"]
    project_dir = manifest["project"].get("project_dir", "project")
    modules = manifest["modules"].get("sequence", [])
    project_path = os.path.join(root, project_dir)

    errors = []
    warnings = []

    # Проверить config.py
    config_path = os.path.join(project_path, "config.py")
    if not os.path.exists(config_path):
        errors.append(CompileError("config", "config.py not found"))
    else:
        err = _check_syntax(config_path, "config")
        if err:
            errors.append(err)
        else:
            cfg_warnings = _validate_config(config_path)
            warnings.extend(cfg_warnings)

    # Проверить helpers.py
    helpers_path = os.path.join(project_path, "helpers.py")
    if not os.path.exists(helpers_path):
        errors.append(CompileError("helpers", "helpers.py not found"))
    else:
        err = _check_syntax(helpers_path, "helpers")
        if err:
            errors.append(err)

    # Проверить каждый модуль
    for mod in modules:
        mod_path = os.path.join(project_path, mod.replace(".", "/") + ".py")
        if not os.path.exists(mod_path):
            errors.append(CompileError(mod, f"file not found: {mod_path}"))
            continue

        err = _check_syntax(mod_path, mod)
        if err:
            errors.append(err)
            continue

        if not _has_build_function(mod_path):
            errors.append(CompileError(mod, "missing build(doc) function"))

        # Проверить __init__.py
        pkg_dir = os.path.dirname(mod_path)
        init_path = os.path.join(pkg_dir, "__init__.py")
        if not os.path.exists(init_path):
            warnings.append(f"{mod}: missing __init__.py in {os.path.basename(pkg_dir)}/")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def compile_and_build(manifest, export_dir=None):
    """Полный цикл: validate → build → export.

    Returns:
        dict: combined result
    """
    from . import engine

    print("=" * 50)
    print("  CADFORGE COMPILE")
    print("=" * 50)

    # Phase 1: Validate
    t0 = time.time()
    print("\n  Phase 1: Static analysis...")
    val = validate(manifest)
    t1 = time.time()
    print(f"    Checked {len(manifest['modules'].get('sequence', []))} modules in {t1-t0:.2f}s")

    for w in val["warnings"]:
        print(f"    WARN: {w}")
    for e in val["errors"]:
        print(f"    ERROR: {e}")

    if not val["valid"]:
        print("\n  COMPILE FAILED — fix errors above")
        return {
            "success": False,
            "phase": "validate",
            "errors": [str(e) for e in val["errors"]],
            "warnings": val["warnings"],
        }

    print(f"    ✓ Validation passed")

    # Phase 2+3: Build + Export
    print("\n  Phase 2: Building geometry (FreeCADCmd headless)...")
    t2 = time.time()
    build_result = engine.build_project(manifest, export_dir)
    t3 = time.time()

    if not build_result["success"]:
        print(f"\n  BUILD FAILED")
        if build_result["stderr"]:
            for line in build_result["stderr"].strip().split("\n")[-10:]:
                print(f"    {line}")
        return {
            "success": False,
            "phase": "build",
            "errors": [build_result["stderr"]],
            "warnings": val["warnings"],
            "stdout": build_result["stdout"],
        }

    # Вывести stdout билда
    for line in build_result["stdout"].strip().split("\n"):
        print(f"    {line}")

    print(f"\n    Build + export: {t3-t2:.2f}s")
    print(f"    Objects exported: {len(build_result['objects'])}")
    print(f"    Output: {build_result['export_dir']}")

    return {
        "success": True,
        "phase": "complete",
        "errors": [],
        "warnings": val["warnings"],
        "objects": build_result["objects"],
        "export_dir": build_result["export_dir"],
        "build_time": t3 - t2,
        "validate_time": t1 - t0,
    }


def _check_syntax(filepath, module_name):
    """Проверить синтаксис Python-файла через ast.parse."""
    try:
        with open(filepath, "r") as f:
            source = f.read()
        ast.parse(source, filename=filepath)
        return None
    except SyntaxError as e:
        return CompileError(module_name, f"SyntaxError: {e.msg}", e.lineno)


def _has_build_function(filepath):
    """Проверить наличие функции build(doc) в модуле."""
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "build":
            # Проверить что принимает хотя бы 1 аргумент
            args = node.args
            total = len(args.args) + len(args.posonlyargs)
            if total >= 1:
                return True
    return False


def _validate_config(config_path):
    """Проверить значения в config.py на здравость."""
    warnings = []
    with open(config_path, "r") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    # Проверить что размеры не отрицательные
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                        if node.value.value < 0 and not name.startswith("COL_"):
                            warnings.append(
                                f"config.{name} = {node.value.value} (negative value)"
                            )
    return warnings
