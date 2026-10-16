#!/usr/bin/env python3
"""Thin wrapper — runs apply_desk_feel_fix.py."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "apply_desk_feel_fix.py"), run_name="__main__")
