"""Tests for cadforge.compiler — static analysis phase."""
import os
import tempfile

import pytest

from cadforge.compiler import _check_syntax, _has_build_function, validate
from cadforge.manifest import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# validate() on the real project
# ---------------------------------------------------------------------------

def test_validate_current_project():
    """validate() should pass on the existing project tree."""
    m = load(ROOT)
    result = validate(m)
    assert result["valid"], f"Validation failed: {result['errors']}"
    assert isinstance(result["warnings"], list)


# ---------------------------------------------------------------------------
# _check_syntax
# ---------------------------------------------------------------------------

def test_check_syntax_valid():
    """A syntactically correct file should return None."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("x = 1 + 2\n")
        f.flush()
        path = f.name
    try:
        assert _check_syntax(path, "test_mod") is None
    finally:
        os.unlink(path)


def test_check_syntax_invalid():
    """A file with a syntax error should return a CompileError."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def oops(\n")
        f.flush()
        path = f.name
    try:
        err = _check_syntax(path, "bad_mod")
        assert err is not None
        assert "bad_mod" in str(err)
        assert "SyntaxError" in str(err)
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# _has_build_function
# ---------------------------------------------------------------------------

def test_has_build_function_present():
    """Detect a valid build(doc) function."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def build(doc):\n    pass\n")
        f.flush()
        path = f.name
    try:
        assert _has_build_function(path) is True
    finally:
        os.unlink(path)


def test_has_build_function_missing():
    """Return False when no build function exists."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def helper():\n    pass\n")
        f.flush()
        path = f.name
    try:
        assert _has_build_function(path) is False
    finally:
        os.unlink(path)


def test_has_build_function_no_args():
    """build() with zero arguments should not count."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def build():\n    pass\n")
        f.flush()
        path = f.name
    try:
        assert _has_build_function(path) is False
    finally:
        os.unlink(path)
