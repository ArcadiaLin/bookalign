---
name: bookalign-labse
description: Agent-oriented EPUB inspection, extraction, chapter matching, local chapter alignment, and alignment diagnostics for bilingual books. Use when Codex needs to work with one or two EPUB files step by step, inspect chapter structure, search text, suggest chapter matches, align a chapter pair or short chapter range, review alignment warnings, or validate Bookalign runtime setup instead of attempting unsafe whole-book automation.
---

# Bookalign LaBSE

Use this skill through the standard skill layout:

- `scripts/` for deterministic checks and repeatable command-line helpers.
- `references/` for workflow rules, tool selection, and exact API semantics.
- root Python modules as implementation resources behind those workflows.

Prefer chapter-by-chapter workflows. Do not default to one-shot whole-book alignment.

## Confirm the execution environment before running anything

This skill must not assume the host matches the author's local machine. Before running scripts or importing modules, ask the user to confirm:

- the repository root or installed skill root
- the Python entrypoint they want used for this task
- whether a project-local virtualenv is already prepared
- whether they want `uv run python ...` or a direct interpreter
- the local LaBSE model path, if local alignment is expected
- whether remote inference is allowed, and whether `HF_TOKEN` is configured
- the artifacts/output directory for reviewable runs

Interpreter priority for examples in this skill:

1. user-provided project environment such as `uv run python` or `<project>/.venv/bin/python`
2. `python3`
3. `python`, but only if the user confirms it exists on this machine

Path rule:

- always anchor commands to the skill directory itself, not to similarly named repo-root `scripts/` or `references/` directories
- prefer placeholders such as `<repo-root>/skills/bookalign-labse` or `<skill-root>` over machine-specific absolute paths

## Use the stable entry points

For environment validation, prefer:

- `<python-entry> <skill-root>/scripts/check_environment.py`
- `<python-entry> <skill-root>/scripts/smoke_test.py`

Read the JSON output from `scripts/check_environment.py` before alignment. Treat these fields as the decision surface:

- `recommended_backend`
- `recommended_model_name`
- `recommended_device`
- `preferred_local_model`

For EPUB extraction audit samples, prefer:

- `<python-entry> <skill-root>/scripts/epub_debug_report.py --book <path-or-pattern> ...`

For in-process Python work, add the skill directory itself to `sys.path`, then import root modules directly.

```python
import sys
from pathlib import Path

SKILL_ROOT = Path("<skill-root>")
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

import api
import service
from align.bertalign_adapter import BertalignAdapter
```

Prefer these Python files as the public surface:

- `api.py`: extract one EPUB and load/save extraction JSON.
- `service.py`: list chapters, preview text, inspect structure, search text, match chapters, align local chapter pairs, inspect diagnostics.
- `align/bertalign_adapter.py`: choose and configure the Bertalign backend.

Treat `epub/`, `models/`, `pipeline.py`, and `vendor/` as implementation resources. Read them only when the public APIs are insufficient.

When the task is full-book production rather than one-off inspection, prefer `<python-entry> <skill-root>/scripts/build_bilingual_epub.py ...` and read [references/production-workflow.md](./references/production-workflow.md) first.

## Follow the normal workflow

1. Ask the user to confirm interpreter, model path, remote-inference policy, and output directory.
2. Run `<python-entry> <skill-root>/scripts/check_environment.py` before choosing an alignment backend.
3. Extract one or two books with `api.extract_book(...)`.
4. Inspect chapters with `service.list_book_chapters(...)`.
5. Run a chapter-consistency self-check before trusting `chapter_id`-based matching.
6. Preview suspicious chapters with `service.get_chapter_preview(...)` or `service.get_chapter_structure(...)`.
7. Search anchor text with `service.search_book_text(...)` or `service.locate_text(...)`.
8. Suggest likely chapter matches with `service.suggest_chapter_matches(...)`.
9. Align one chapter pair or a short chapter range at a time.
10. Review diagnostics, unmatched content, and warnings before continuing.
11. Call `service.review_unaligned_segments(...)` after each alignment round to inspect all remaining one-sided source/target content before deciding whether to align more, reslice, or leave it unmatched.

If the user asks for broad automation, still keep explicit review checkpoints between extraction, chapter matching, and alignment.

For controlled whole-book production, use this template:

1. Check environment.
2. Extract both books.
3. Audit chapters and spine documents.
4. Compare chapter listings against sampled `sentence_segments` before accepting chapter ids as anchors.
5. Detect mixed-content or drifted chapters.
6. Produce a chapter-slice plan only for clean, unambiguous slices.
7. Align each clean slice.
8. Run diagnostics and export review artifacts.
9. Build preview/review outputs.
10. Build the final EPUB.

Important execution boundary:

- production alignment now requires an explicit `slice_plan`
- implicit chapter-by-index whole-book pairing is not supported
- chapter matching suggestions remain inspection aids, not production defaults

## Choose the alignment backend conservatively

Use the local backend when local dependencies are installed and local inference is acceptable.

When the environment check reports `recommended_backend="local_cuda"` or `recommended_backend="local_cpu"`, prefer the explicit local model path from `recommended_model_name` instead of a registry name like `sentence-transformers/LaBSE`. This avoids accidental network/model-resolution behavior on first load.

```python
aligner = BertalignAdapter(
    model_name="<local-labse-model-path>",
    model_backend="local",
    device=device,
    src_lang="ja",
    tgt_lang="zh",
)
```

Use Hugging Face inference only when local runtime dependencies are missing or the user prefers remote inference, and only if `HF_TOKEN` is configured.

```python
aligner = BertalignAdapter(
    model_name="rasa/LaBSE",
    model_backend="hf_inference",
    hf_api_url="https://router.huggingface.co/hf-inference/models/rasa/LaBSE/pipeline/feature-extraction",
    hf_api_token_env="HF_TOKEN",
    device="cpu",
    src_lang="ja",
    tgt_lang="zh",
)
```

Never silently continue if no usable local or remote model path exists.

If proxy or mirror variables such as `HF_ENDPOINT`, `HTTP_PROXY`, or `HTTPS_PROXY` are set, mention them when diagnosing why a nominally local setup still tries to resolve remote artifacts.

## Run a chapter-consistency self-check before alignment

Do not treat `chapter_id` as a stable cross-view anchor. It is a useful lookup key inside one extraction, but it can drift relative to visible headings and the effective ownership of sentence records.

Before aligning, compare:

- `service.list_book_chapters(...)` summaries
- `service.get_chapter_preview(...)` visible opening text
- `service.get_chapter_structure(...)` heading candidates
- a direct sample from `extraction.sentence_segments` or `service.sample_sentences(...)`

Goal of the self-check:

- confirm that the first sentence records attributed to a chapter actually belong to the visible body section you intend to align
- catch cases where notes, commentary, chronology, or a prior body fragment were merged into the same `chapter_id`
- detect cases where paragraph indices or body sub-sections reset inside one visible chapter bucket

If `list_book_chapters(...)` and sentence-level samples disagree about where the body starts, stop and inspect. Do not begin alignment on the assumption that `chapter_id` alone is authoritative.

## Handle chapter drift before trusting match suggestions

Books with contents, chronology sections, translator notes, split prefaces, or other front matter may shift visible chapter numbering by one or more chapters. In these cases, treat `service.suggest_chapter_matches(...)` as a heuristic proposal only.

Before aligning, verify likely body-start chapters by combining:

- `service.list_book_chapters(...)` for chapter ids and quick previews
- `service.get_chapter_preview(...)` for the first visible body text
- `service.get_chapter_structure(...)` for heading candidates and anomaly counts

Useful practical signals:

- a chapter id like `chapter-iii` may still contain visible text `CHAPTER I`
- a translated chapter id like `第三章` may contain visible heading text `第二章`
- `kind_guess` is helpful, but not authoritative for separating body text from contents, chronology, or appendix-like material

If the first suggested match looks structurally wrong, inspect neighboring chapters before aligning anything.

Current matching model note:

- `pipeline.match_extracted_chapters(...)` uses a simplified raw matcher
- do not expect structured paratext-aware matching modes in the production path
- use slice planning and explicit review instead of relying on automatic chapter filtering

Current production planning note:

- `slice_plan` is only safe when each job can be expressed as a clean `chapter_id` plus monotonic paragraph bounds
- if one `chapter_id` contains multiple body regions, mixed notes, or paragraph-index resets, do not force it into the production API
- in those cases, inspect spine documents and build a reviewed `AlignmentResult` manually or split the content earlier with safer preprocessing

## Keep the right object model in memory

Keep extracted books as `BookExtraction` objects. Keep local alignment results as `AlignmentResult` objects.

For short exploratory work, keep objects in memory.

For long or review-heavy production work, persist intermediate artifacts under `artifacts/`. This is recommended.

Useful artifact types:

- `source_extraction.json`
- `target_extraction.json`
- `slice_manifest.json`
- `alignment.json`
- `alignment_report.json`
- `review.html`
- final EPUB output

Recommended post-round review interface:

- `service.review_unaligned_segments(alignment)` returns all currently unmatched pair blocks and merged unmatched regions, including joined `source_text` and `target_text`, so the agent can inspect everything left out by the previous round and decide whether another alignment pass is warranted

## Load detailed references only when needed

Read [references/workflow.md](./references/workflow.md) when you need the full review-first workflow, backend choice rationale, failure handling, or capability boundaries.

Read [references/tooling.md](./references/tooling.md) when you need the standard script entry points, module layout, validation commands, or canonical-vs-compatibility API guidance.

Read [references/api-reference.md](./references/api-reference.md) when you need exact function signatures, return payload shapes, serialization helpers, alignment inspection utilities, rule-management functions, or example call sequences.

Read [references/production-workflow.md](./references/production-workflow.md) when you need the high-level build script, artifact layout, slice-plan schema, or builder-related production guidance.

Read tests in `tests/` when you need concrete usage examples for service APIs or expected payload shapes.
