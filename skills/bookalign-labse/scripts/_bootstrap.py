"""Shared helpers for skill-local command-line scripts."""

from __future__ import annotations

from pathlib import Path
import sys


def ensure_skill_root() -> Path:
    """Add the skill root to ``sys.path`` and return it."""

    skill_root = Path(__file__).resolve().parents[1]
    skill_root_str = str(skill_root)
    if skill_root_str not in sys.path:
        sys.path.insert(0, skill_root_str)
    return skill_root
