# Repository Guidelines

## Project Structure & Module Organization

Core code lives in `bookalign/`. Use `bookalign/epub/` for EPUB reading, extraction, CFI handling, rebuilding, and debug reporting; `bookalign/align/` for alignment backends and adapters; `bookalign/models/` for shared data types; and `bookalign/cli.py` plus `bookalign/pipeline.py` for entry points and orchestration. Tests live in `tests/`. Committed manual review material is limited to `tests/artifacts/batch_reader_reports/`; other generated artifacts should stay uncommitted. Sample EPUB fixtures are kept in `books/`. Project documentation is maintained in `README.md`, `DESIGN.md`, `STATUS.md`, and `TECHNICAL.md`.

## Build, Test, and Development Commands

This project targets Python 3.12 and uses `uv`.

- `uv sync` installs runtime and dev dependencies from `pyproject.toml` and `uv.lock`.
- `uv run pytest` runs the full test suite.
- `uv run pytest tests/test_splitter.py tests/test_extractor.py -q` runs the main extraction-focused tests quickly.
- `uv run pytest -m integration` runs tests marked `integration` against real EPUB fixtures.
- `uv run python -m bookalign.epub.debug_report --help` shows options for generating manual review reports.

## Coding Style & Naming Conventions

Follow existing Python conventions: 4-space indentation, type-aware code, and small focused modules. Use `snake_case` for functions, variables, and test files; `PascalCase` for classes and dataclasses; and keep CLI-facing names descriptive. Preserve the current package split by responsibility instead of adding large utility files. No formatter is configured yet, so match the surrounding style and keep imports and control flow tidy.

## Testing Guidelines

Tests use `pytest`; integration coverage is labeled with the `integration` marker in `pytest.ini`. Add unit tests beside the relevant feature in `tests/` using `test_<feature>.py` naming. Prefer fixture-driven cases for EPUB parsing edge cases and keep generated artifacts under `tests/artifacts/`, not mixed into source directories. When changing extraction or sentence-splitting behavior, run the targeted pytest command above before running the full suite.

## Commit & Pull Request Guidelines

Recent history shows short, task-focused commit messages, often in Chinese, for example `基本完成extractor的v1开发，接下来进入对齐流程`. Keep commits small and scoped to one change. PRs should describe the user-visible effect, list touched modules, note any fixture or artifact updates, and include sample output or screenshots when changing report generation or EPUB reconstruction behavior.

## Security & Repository Hygiene

Do not commit new copyrighted EPUBs, secrets, or local virtual environment contents. Treat `books/` as local test material and keep additions minimal. Vendor code under `bookalign/vendor/` should only be changed when the upstream integration actually requires it.
