"""Canonical CLI entry point for EPUB extraction audit reports."""

from __future__ import annotations

from _bootstrap import ensure_skill_root


def main() -> None:
    ensure_skill_root()
    from epub.debug_report import main as debug_main

    debug_main()


if __name__ == "__main__":
    main()
