"""Запуск: python -m cadforge build|dev|validate|export"""
import sys
from .cli import main

sys.exit(main() or 0)
