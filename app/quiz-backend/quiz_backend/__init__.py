"""Quiz backend service package."""

from __future__ import annotations

import sys
from pathlib import Path

_COMMON_PATH = Path(__file__).resolve().parents[2] / "backend-common"
if _COMMON_PATH.exists() and str(_COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(_COMMON_PATH))

from .app import create_app

__all__ = ["create_app"]
