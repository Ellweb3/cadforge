#!/bin/bash
# CadForge CLI wrapper
# Usage: ./cadforge.sh build | validate | dev | export
cd "$(dirname "$0")"
exec /Users/ell/.freecad-mcp/venv/bin/python3 -m cadforge "$@"
