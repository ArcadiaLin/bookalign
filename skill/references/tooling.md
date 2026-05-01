# Bookalign Tooling Reference

## Table of Contents

- Standard skill layout
- Canonical scripts
- Python module map
- Canonical APIs and compatibility aliases
- Validation commands

## Standard skill layout

Treat this skill as a standard `SKILL.md + scripts/ + references/` package:

- `SKILL.md`: trigger metadata and the minimal operating guide.
- `scripts/`: deterministic entry points for repeatable checks and audits.
- `references/`: detailed workflow and API documents loaded only when needed.
- root Python modules: implementation resources used by the scripts and by in-process agent code.

The implementation is still intentionally importable as a Python package-like directory. Do not move or rename the existing internal modules unless you are updating every import site and test.

## Canonical scripts

Use these scripts as the preferred command-line entry points:

### `scripts/check_environment.py`

Purpose:

- inspect extraction dependencies
- inspect optional alignment dependencies
- detect Torch/CUDA availability
- detect ready local SentenceTransformer model paths
- detect `HF_TOKEN`
- report proxy or mirror variables that may affect model resolution
- recommend a concrete backend, model name, and device

Typical usage:

```bash
python scripts/check_environment.py
python scripts/check_environment.py --json
```

Read these JSON fields before selecting a backend:

- `recommended_backend`
- `recommended_model_name`
- `recommended_device`
- `preferred_local_model`

Expected meaning:

- `local_cuda`: use the explicit local model path on CUDA
- `local_cpu`: use the explicit local model path on CPU
- `hf_inference`: use Hugging Face inference
- `local_model_missing`: local runtime exists but no ready local model path was detected
- `inspection_only`: only non-alignment workflows are safely ready

### `scripts/smoke_test.py`

Purpose:

- verify that extraction, chapter listing, search, and local stub alignment work end to end
- validate the stable public workflow without requiring heavy Bertalign runtime dependencies

Typical usage:

```bash
python scripts/smoke_test.py
python scripts/smoke_test.py --json
```

### `scripts/epub_debug_report.py`

Purpose:

- generate a Markdown audit report over sampled EPUB extraction cases
- keep the CLI in `scripts/` while reusing the implementation in `epub/debug_report.py`

Typical usage:

```bash
python scripts/epub_debug_report.py --book /path/to/book.epub
python scripts/epub_debug_report.py --book '*.epub' --test-type mixed --granularity sentence
```

## Python module map

Prefer these modules as the stable surface:

- `api.py`: single-book extraction and record access
- `service.py`: main agent-facing browsing, matching, alignment, and diagnostics APIs
- `align/bertalign_adapter.py`: backend selection and Bertalign configuration

Treat these as implementation resources:

- `pipeline.py`: sentence-chapter extraction and chapter-matching internals
- `epub/`: low-level EPUB reading, extraction, CFI, builders, and sentence splitting
- `models/`: data classes and structural types
- `vendor/bertalign/`: vendored alignment backend

## Canonical APIs and compatibility aliases

Prefer these names in new workflows:

- `service.list_book_chapters(...)`
- `service.get_chapter_text(...)`
- `service.list_builder_warnings(...)`

Interpret these fields conservatively:

- `service.get_aligned_pairs(...)[*]["score"]` is not a semantic confidence score
- `service.list_book_chapters(...)[*]["kind_guess"]` is a heuristic hint, not a reliable classifier for body-vs-front-matter decisions

These names exist for compatibility and should not be treated as primary tools:

- `service.list_extracted_chapters(...)` -> alias of `list_book_chapters(...)`
- `service.get_extracted_segments(...)` -> alias of `get_chapter_text(...)`
- `service.list_warnings(...)` -> alias of `list_builder_warnings(...)`

Keep the compatibility aliases unless you are ready to update all call sites, docs, and tests in one change.

## Validation commands

Representative validation commands for this skill:

```bash
python skill/scripts/check_environment.py --json
python skill/scripts/smoke_test.py --json
uv run pytest skill/tests -q
```

Use `scripts/smoke_test.py` for fast verification after documentation or wiring changes. Use `uv run pytest skill/tests -q` before finishing any structural change that might affect imports, extraction behavior, or public service APIs.
