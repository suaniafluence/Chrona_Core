"""Pytest configuration for backend tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the backend source directory is importable as the ``src`` package when
# tests are executed from the repository root. This mirrors the behaviour when
# running ``pytest`` from within ``backend/`` locally.
BACKEND_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_DIR / "src"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
