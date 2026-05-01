---
name: bookalign
description: Agent-oriented EPUB inspection, extraction, chapter matching, local chapter alignment, and alignment diagnostics for bilingual books. Use when Codex needs to work with one or two EPUB files step by step, inspect chapter structure, search text, suggest chapter matches, align a chapter pair or short chapter range, review alignment warnings, or validate Bookalign runtime setup instead of attempting unsafe whole-book automation.
---

# Bookalign

Use this skill through the standard skill layout:

- `scripts/` for deterministic checks and repeatable command-line helpers.
- `references/` for workflow rules, tool selection, and exact API semantics.
- root Python modules as implementation resources behind those workflows.

Prefer chapter-by-chapter workflows. Do not default to one-shot whole-book alignment.

## Use the stable entry points

For environment validation, prefer:

- `python scripts/check_environment.py`
- `python scripts/smoke_test.py`

Read the JSON output from `scripts/check_environment.py` before alignment. Treat these fields as the decision surface:

- `recommended_backend`
- `recommended_model_name`
- `recommended_device`
- `preferred_local_model`

For EPUB extraction audit samples, prefer:

- `python scripts/epub_debug_report.py --book <path-or-pattern> ...`

For in-process Python work, add the skill directory itself to `sys.path`, then import root modules directly.

```python
import sys
from pathlib import Path

SKILL_ROOT = Path("/root/projs/bookalign/skill")
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

When the task is full-book production rather than one-off inspection, prefer `python scripts/build_bilingual_epub.py ...` and read [references/production-workflow.md](./references/production-workflow.md) first.

## Follow the normal workflow

1. Run `scripts/check_environment.py` before choosing an alignment backend.
2. Extract one or two books with `api.extract_book(...)`.
3. Inspect chapters with `service.list_book_chapters(...)`.
4. Preview suspicious chapters with `service.get_chapter_preview(...)` or `service.get_chapter_structure(...)`.
5. Search anchor text with `service.search_book_text(...)` or `service.locate_text(...)`.
6. Suggest likely chapter matches with `service.suggest_chapter_matches(...)`.
7. Align one chapter pair or a short chapter range at a time.
8. Review diagnostics, unmatched content, and warnings before continuing.

If the user asks for broad automation, still keep explicit review checkpoints between extraction, chapter matching, and alignment.

For controlled whole-book production, use this template:

1. Check environment.
2. Extract both books.
3. Audit chapters and spine documents.
4. Detect mixed-content or drifted chapters.
5. Produce a chapter-slice plan.
6. Align each clean slice.
7. Run diagnostics and export review artifacts.
8. Build preview/review outputs.
9. Build the final EPUB.

Important execution boundary:

- production alignment now requires an explicit `slice_plan`
- implicit chapter-by-index whole-book pairing is not supported
- chapter matching suggestions remain inspection aids, not production defaults

## Choose the alignment backend conservatively

Use the local backend when local dependencies are installed and local inference is acceptable.

When the environment check reports `recommended_backend="local_cuda"` or `recommended_backend="local_cpu"`, prefer the explicit local model path from `recommended_model_name` instead of a registry name like `sentence-transformers/LaBSE`. This avoids accidental network/model-resolution behavior on first load.

```python
aligner = BertalignAdapter(
    model_name="/root/models/LaBSE",
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

## Load detailed references only when needed

Read [references/workflow.md](./references/workflow.md) when you need the full review-first workflow, backend choice rationale, failure handling, or capability boundaries.

Read [references/tooling.md](./references/tooling.md) when you need the standard script entry points, module layout, validation commands, or canonical-vs-compatibility API guidance.

Read [references/api-reference.md](./references/api-reference.md) when you need exact function signatures, return payload shapes, serialization helpers, alignment inspection utilities, rule-management functions, or example call sequences.

Read [references/production-workflow.md](./references/production-workflow.md) when you need the high-level build script, artifact layout, slice-plan schema, or builder-related production guidance.

Read tests in `tests/` when you need concrete usage examples for service APIs or expected payload shapes.
