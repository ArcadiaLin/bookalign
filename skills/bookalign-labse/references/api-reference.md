# Bookalign LaBSE API Reference

## Table of Contents

- Purpose
- Import pattern
- Core objects
- Module selection
- Tooling and canonical API names
- `api.py`
- `service.py`
- `align/bertalign_adapter.py`
- Serialization helpers
- Example workflow

## Purpose

Use this document when the task requires exact API selection, parameter details, return payload expectations, or composition of multiple Bookalign tools in one workflow.

Prefer `service.py` for agent-facing operations. Drop to `api.py` when you need lower-level extraction access or direct record retrieval. Treat most underscored helpers as internal.

## Import Pattern

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

## Core Objects

### `BookExtraction`

Serializable extraction result for one EPUB.

Important fields:

- `language`: language code used during sentence splitting.
- `extract_mode`: current default is usually `filtered_preserve`.
- `default_granularity`: `sentence` or `paragraph`.
- `chapters`: ordered `ChapterInfo` list.
- `sentence_segments`: ordered sentence `SegmentRecord` list.
- `paragraph_segments`: ordered paragraph `SegmentRecord` list.
- `source_path`: original EPUB path when extracted from a file.

### `ChapterInfo`

Per-chapter metadata.

Important fields:

- `chapter_id`: agent-facing lookup key within one extraction, not a cross-view stability guarantee.
- `chapter_idx`: inferred chapter order index.
- `spine_idx`: EPUB spine index.
- `title`
- `label`
- `is_paratext`
- `sentence_count`
- `paragraph_count`

### `SegmentRecord`

Wrapper that combines a `Segment` plus chapter metadata.

Important fields:

- `segment`
- `chapter_id`
- `chapter_title`
- `granularity`

### `Segment`

Atomic text unit used by extraction and alignment.

Important fields:

- `text`
- `cfi`
- `chapter_idx`
- `paragraph_idx`
- `sentence_idx`
- `paragraph_cfi`
- `has_jump_markup`
- `is_note_like`
- `alignment_role`
- `paratext_kind`
- `jump_fragments`
- `spans`

### `AlignmentResult`

Alignment result over one chapter pair or a short chapter range.

Important fields:

- `pairs`: list of `AlignedPair`
- `source_lang`
- `target_lang`
- `granularity`
- `extract_mode`
- `retained_source_segments`
- `retained_target_segments`

## Module Selection

Use:

- `service.py` for browsing, chapter matching, alignment, diagnostics, reports, rules, and artifact IO.
- `production.py` for high-level multi-artifact production workflows.
- `api.py` for extraction primitives and direct chapter record access.
- `align/bertalign_adapter.py` for model/backend selection.
- `extraction_json.py` and `alignment_json.py` for direct serialization helpers.
- `pipeline.py` only when you need chapter matching internals or sentence-chapter extraction.

Avoid:

- calling underscored helpers directly unless you are extending internals.
- treating chapter match confidence as a calibrated semantic confidence score.
- running whole-book alignment by default.

## Tooling and Canonical API Names

Prefer the standard scripts for deterministic checks:

- `scripts/check_environment.py`
- `scripts/smoke_test.py`
- `scripts/epub_debug_report.py`

Before using them, ask the user to confirm `<python-entry>`, `<skill-root>`, local model path, and whether remote inference is allowed.

Prefer these service APIs in new workflows:

- `list_book_chapters`
- `get_chapter_text`
- `list_builder_warnings`

Treat these as compatibility aliases:

- `list_extracted_chapters` -> same as `list_book_chapters`
- `get_extracted_segments` -> same as `get_chapter_text`
- `list_warnings` -> same as `list_builder_warnings`

## `api.py`

Low-level extraction and record access.

### `load_epub(path)`

Read an EPUB and return an `ebooklib.epub.EpubBook`.

Use when:

- you need the parsed book object itself.
- you want to extract from an already-loaded book later.

### `extract_book(source, *, language, granularity="sentence", extract_mode="filtered_preserve")`

Extract one EPUB into a `BookExtraction`.

Parameters:

- `source`: path-like or `EpubBook`.
- `language`: required. Drives sentence splitting.
- `granularity`: `sentence` or `paragraph`.
- `extract_mode`: currently defaults to `filtered_preserve`.

Returns:

- `BookExtraction`

Use when:

- starting almost every workflow.

Typical call:

```python
source = api.extract_book("/path/source.epub", language="ja")
target = api.extract_book("/path/target.epub", language="zh")
```

### `save_extraction_json(extraction, path)`

Serialize one extraction to JSON and return the output `Path`.

Use when:

- the user wants a persistent extraction artifact.
- you need repeatable offline inspection.

### `load_extraction_json(path)`

Load an extraction artifact back into a `BookExtraction`.

### `list_chapters(extraction)`

Return ordered `ChapterInfo` objects.

Use when:

- you want object-level chapter metadata instead of service payload dicts.

### `get_chapter_records(extraction, chapter_ref, *, granularity=None, include_retained=True, limit=None, offset=0)`

Return ordered `SegmentRecord` items for a chapter.

Parameters:

- `chapter_ref`: `chapter_id`, `chapter_idx`, or `spine_idx`.
- `granularity`: defaults to extraction default when `None`.
- `include_retained`: include non-alignable retained text.
- `limit`, `offset`: pagination-style slicing.

Use when:

- you need raw record objects rather than JSON-like payloads.

### `get_chapter_count(extraction, chapter_ref, *, granularity=None, include_retained=True)`

Return the number of records for one chapter under a specific granularity/filter.

### Legacy convenience wrappers in `api.py`

This file also exposes several dict-returning wrappers with the same names and behavior as `service.py`, including:

- `list_book_chapters`
- `get_chapter_preview`
- `get_chapter_text`
- `get_chapter_structure`
- `search_book_text`
- `list_extracted_chapters`
- `get_extracted_segments`
- `get_segment`
- `resolve_cfi`
- `locate_text`
- `get_segment_cfi`

Prefer the `service.py` versions for agent work because that file is the canonical service surface.

## `service.py`

Primary agent-facing tool surface.

### Chapter browsing and text inspection

#### `preview_spine_documents(extraction)`

Return spine order, file names, titles, character counts, and text previews for each readable XHTML document.

#### `preview_document_raw(extraction, spine_idx, max_chars=4000)`

Return raw XHTML content for one spine document.

#### `preview_document_rendered(extraction, spine_idx, mode="html", max_chars=4000)`

Return a simplified rendered preview for one spine document.

Supported `mode`:

- `html`
- `markdown`

#### `list_book_chapters(extraction, view="summary")`

Return chapter list payload:

- `book_id`
- `extraction_id`
- `chapters`

Each chapter item includes:

- `chapter_id`
- `spine_item_id`
- `spine_index`
- `title`
- `label`
- `kind_guess`
- `preview_text_100`
- `char_count`
- `paragraph_count`
- `sentence_count_estimate`

Notes:

- `kind_guess` is heuristic only. Do not trust it as a strong classifier for contents, chronology, preface, or other front-matter cases.
- For books with chapter drift, compare `chapter_id` against the visible heading text surfaced by `preview_text_100` and `get_chapter_preview(...)`.
- Do not assume `chapter_id` and sentence-level ownership stay perfectly aligned; sample `sentence_segments` when the first body match matters.

Use when:

- choosing which chapter to inspect next.

#### `get_chapter_preview(extraction, chapter_id, max_chars=300)`

Return a short preview for one chapter.

Use when:

- triaging chapter identity quickly.

#### `get_chapter_text(extraction, chapter_id, granularity="paragraph", include_retained=True, limit=None, offset=0)`

Return detailed chapter text payload with:

- chapter metadata
- requested granularity
- segment list

Use when:

- you need actual extracted text units.
- you need pagination over a large chapter.

#### `get_chapter_structure(extraction, chapter_id)`

Return structure summary with:

- `paragraph_count`
- `sentence_count`
- `footnote_count`
- `heading_candidates`
- `poetry_line_count`
- `anomaly_segments`

Use when:

- checking whether a chapter is safe to align.

#### `locate_heading_boundaries(extraction, chapter_id)`

Return heading-like paragraph boundaries inside a single extracted chapter.

Use when:

- producing a slice plan for a dirty chapter.

#### `detect_mixed_content_chapters(extraction)`

Return chapters that appear to mix body text with notes, TOC residue, or repeated heading blocks.

#### `search_book_text(extraction, query, scope="all")`

Supported `scope` values:

- `all`
- `chapter`
- `body`

Returns matching paragraph-based hits with chapter and segment ids.

Use when:

- locating anchor terms across the book.

#### `locate_text(extraction, text_query, chapter_id=None)`

Return matches across the whole book or within one chapter, including per-hit position offsets.

Use when:

- you need chapter-local search with positions.

#### `get_segment(extraction, segment_id)`

Return the fully expanded segment payload for a stable segment id.

#### `get_segment_cfi(extraction, segment_id)`

Return just:

- `segment_id`
- `cfi`
- `paragraph_cfi`

#### `resolve_cfi(extraction, cfi)`

Resolve a CFI back to EPUB-level location information and matching extracted segments.

#### `extract_text_by_cfi(extraction, cfi)`

Extract raw text directly from a CFI against the EPUB book object.

#### `compare_cfi_ranges(extraction, cfi_a, cfi_b)`

Return ordering relation:

- `same`
- `before`
- `after`
- `unknown`

### Extraction aliases

These are light aliases for naming clarity:

- `list_extracted_chapters(extraction)` -> same as `list_book_chapters`
- `get_extracted_segments(extraction, chapter_id, granularity="sentence", include_retained=True)` -> same as `get_chapter_text`

### Chapter matching

#### `suggest_chapter_matches(source_extraction, target_extraction, strategy="heuristic")`

Return suggested chapter pairs:

- `source_extraction_id`
- `target_extraction_id`
- `strategy`
- `matches`

Each match includes:

- `source_chapter_id`
- `target_chapter_id`
- `confidence`

Notes:

- only `heuristic` is supported.
- confidence is heuristic ranking output, not a calibrated semantic probability.
- falls back to a simpler matcher if source paths are unavailable.
- treat the output as a review queue, not as proof that the chapters line up.
- if chapter numbering appears offset, inspect adjacent chapters manually before aligning.

### Alignment execution

### Chapter slicing and cleanup

#### `slice_chapter(extraction, chapter_id, start_para, end_para, granularity="paragraph", include_retained=True, exclude_note_like=False)`

Return a bounded paragraph/sentence window from one chapter.

#### `split_chapter_by_heading(extraction, chapter_id, headings, granularity="paragraph")`

Return matching heading boundaries plus suggested paragraph slices.

#### `split_chapter_by_predicate(extraction, chapter_id, rule, granularity="paragraph")`

Return regex-matched boundaries plus suggested paragraph slices.

#### `exclude_note_like_segments(extraction, chapter_id, granularity="paragraph")`

Return kept-vs-removed segments for note-like cleanup.

#### `align_chapter_pair(source_extraction, target_extraction, source_chapter_id, target_chapter_id, granularity="sentence", aligner=None)`

Align one source chapter to one target chapter.

Returns:

- `AlignmentResult`

Use when:

- doing the normal safe alignment workflow.

#### `align_chapter_ranges(source_extraction, target_extraction, source_chapter_ids, target_chapter_ids, granularity="sentence", aligner=None)`

Align short chapter ranges by flattening the selected records.

Use when:

- one logical chapter was split differently across editions/translations.

Do not use this as a whole-book batch shortcut unless the user explicitly accepts the risk.

### Alignment inspection

#### `inspect_alignment(alignment)`

Return lightweight stats:

- `alignment_id`
- `pair_count`
- `source_unmatched_pairs`
- `target_unmatched_pairs`
- `skip_ratio`

#### `get_alignment_summary(alignment)`

Return high-level counts and languages.

#### `get_aligned_pairs(alignment, offset=0, limit=100)`

Return paginated aligned pairs with:

- `pair_id`
- `score`
- brief source segment list
- brief target segment list

Notes:

- `score` is not a calibrated semantic confidence score.
- the current adapter path commonly returns a placeholder value of `1.0`.
- rely on `inspect_alignment`, unmatched-segment inspection, text review, and warning inspection instead.

#### `get_unmatched_segments(alignment, side="source")`

Return only one-sided unmatched pairs.

Supported `side`:

- `source`
- `target`

#### `review_unaligned_segments(alignment)`

Return a review-oriented payload for all currently unmatched content in one call.

Top-level fields:

- `alignment_id`
- `pair_count`
- `items`: every one-sided unmatched pair with `pair_id`, `side`, brief segments, `source_text`, and `target_text`
- `regions`: merged consecutive unmatched ranges within one chapter side

Use when:

- the agent should inspect all leftover source-only and target-only content after one alignment round
- the next step depends on deciding whether to realign, reslice, or leave a region unmatched

#### `get_alignment_block_text(alignment, pair_id)`

Return joined source and target text for one alignment pair.

Use when:

- showing a human-readable comparison for review.

#### `sample_alignment_pairs(alignment, strategy="head/middle/tail", count=9)`

Return representative pair samples for fast human review.

#### `find_alignment_outliers(alignment)`

Return suspicious pairs such as empty-side matches, 1:n or n:1 pairs, long pairs, or zero-score pairs.

#### `group_unmatched_by_region(alignment)`

Group consecutive unmatched pairs into chapter-local regions.

#### `compare_alignment_density(alignment)`

Summarize pair counts, segment counts, unmatched counts, and skip ratios by chapter region.

### Alignment artifacts

#### `export_alignment_json(alignment, output_path)`

Write alignment JSON and return:

- `artifact_id`
- `path`
- `alignment_id`

#### `read_alignment_artifact(path, view="summary")`

Supported `view`:

- `summary`
- `pairs`
- `stats`

Use when:

- reviewing a saved artifact without rebuilding it in memory first.

#### `export_review_html(alignment, output_path)`

Write a local HTML review page summarizing alignment statistics, warnings, outliers, and sample pairs.

#### `export_review_html_from_artifact(path, output_path)`

Load a saved alignment JSON, then write the same HTML review page.

### Builder-preview utilities

These help inspect downstream writeback/build behavior without committing to a full builder pipeline.

#### `preview_build_plan(alignment, mode="source_layout", writeback_mode="paragraph")`

Return chapter indices touched and warning count.

#### `build_single_chapter_preview(alignment, source_chapter_id, target_chapter_id=None, mode="html")`

Return HTML preview for one aligned chapter region.

Only `html` mode is supported.

#### `list_builder_warnings(alignment)`

Return builder-related warnings such as:

- missing source CFI
- jump markup present
- unmatched side

#### `list_warnings(alignment)`

Alias for `list_builder_warnings`.

### Builder entry points

#### `build_bilingual_epub_from_alignment(alignment, source_extraction, target_extraction, output_path, ...)`

Build the final EPUB from in-memory extraction objects plus an `AlignmentResult`.

Important controls:

- `builder_mode`
- `writeback_mode`
- `layout_direction`
- `include_note_appendix`
- `include_extra_target_appendix`

#### `build_bilingual_epub_from_alignment_artifact(path, source_extraction, target_extraction, output_path, ...)`

Build the final EPUB from a saved alignment JSON artifact.

### Sampling, language guesses, and anomaly detection

#### `sample_sentences(extraction, chapter_id=None, count=10)`

Return a small segment sample for quick inspection.

#### `guess_language(extraction, sample_size=20)`

Return a heuristic language guess based on script detection.

Use when:

- checking whether the extraction language setting looks plausible.

#### `detect_book_features(extraction)`

Return book-level flags such as:

- many footnotes
- poetry
- vertical punctuation
- fragmented spans
- TOC-like content

#### `detect_chapter_anomalies(extraction)`

Return only chapters with notable structural anomalies.

#### `generate_book_report(extraction)`

Combine chapters, feature detection, and chapter anomalies into one report.

### Rule management

These rules are lightweight in-memory regex-oriented helpers. They do not represent a durable workflow engine.

Supported rule types:

- `note_detection`
- `poetry_segmentation`
- `chapter_boundary`
- `paratext_classification`
- `sentence_split_override`
- `inline_cleanup`

#### `list_rules(rule_type=None)`

Return all registered rules or only one type.

#### `test_rule(rule_type, rule_content, sample_input)`

Return whether a regex-like rule matches a sample input.

#### `register_rule(rule_type, rule_content, scope="session")`

Create and store a rule, then return:

- `rule_id`
- `rule_type`
- `rule_content`
- `scope`
- `enabled`

#### `enable_rules(session_id, rule_ids)`

Enable a set of rule ids for one session.

#### `disable_rule(rule_id)`

Mark a rule as disabled.

#### `explain_rule_hit(extraction, chapter_id, rule_id)`

Search a chapter and return matching segments for the selected rule.

### Trace and report helpers

#### `generate_alignment_report(alignment)`

Combine:

- summary
- inspection
- warnings

#### `trace_segment(extraction, segment_id)`

Return location/debug metadata for one segment.

#### `trace_builder_anchor(alignment, pair_id)`

Explain which source anchor drives downstream builder anchoring.

## `align/bertalign_adapter.py`

Alignment backend adapter.

### `BertalignAdapter(...)`

Constructor parameters:

- `model_name`
- `device`
- `model_backend`
- `hf_api_url`
- `hf_api_token`
- `hf_api_token_env`
- `hf_request_timeout`
- `max_align`
- `top_k`
- `win`
- `skip`
- `margin`
- `len_penalty`
- `src_lang`
- `tgt_lang`
- `default_score`

Backends:

- `local`
- `hf_inference`

Language aliases normalize several Chinese variants to `zh`.

Backend guidance:

- when a ready local model path exists, prefer a direct user-confirmed local path such as `<local-labse-model-path>` over a registry identifier like `sentence-transformers/LaBSE`.
- use `scripts/check_environment.py --json` to choose `model_backend`, `model_name`, and `device` together.

### `aligner.align(src_texts, tgt_texts)`

Input:

- `src_texts`: `list[str]`
- `tgt_texts`: `list[str]`

Output:

- `list[tuple[list[int], list[int], float]]`

Behavior:

- returns empty list for empty input.
- raises `RuntimeError` when vendor runtime dependencies are missing.
- configures the vendored `bertalign` module before each run.

Use when:

- you want to pass a specific aligner instance into `service.align_chapter_pair` or `service.align_chapter_ranges`.

## Serialization Modules

## `production.py`

High-level persisted-artifact workflow helpers.

Stable functions:

- `run_bilingual_production(...)`
- `align_from_slice_plan(...)`
- `build_bilingual_epub_from_alignment(...)`
- `build_bilingual_epub_from_alignment_json(...)`
- `write_json(path, payload)`

### `extraction_json.py`

Use directly only when you want explicit control over extraction artifact serialization.

Stable functions:

- `save_extraction_result(extraction, path)`
- `load_extraction_result(path)`

### `alignment_json.py`

Use directly only when you want explicit control over alignment artifact serialization.

Stable functions:

- `save_alignment_result(alignment, path)`
- `load_alignment_result(path)`

## `pipeline.py`

Semi-internal helpers used by extraction and chapter matching.

Stable-enough public functions:

### `extract_sentence_chapters(book, *, language, extract_mode="filtered_preserve")`

Return sentence-level `ExtractedChapter` objects for readable spine docs.

### `match_extracted_chapters(source_chapters, target_chapters, *, chapter_match_mode="raw")`

Return `ChapterMatch` list.

Supported `chapter_match_mode`:

- `raw`

Notes:

- `structured` chapter filtering is no longer part of the current execution path.
- chapter matching is intentionally lightweight and should be treated as a suggestion mechanism.
- use explicit `slice_plan` production jobs for final runs.

Use when:

- you need direct access to matching internals outside the higher-level service wrapper.

Avoid depending on the rest of `pipeline.py` unless you are changing chapter matching behavior.

## `production.py`

### `run_bilingual_production(...)`

High-level multi-artifact production entry point.

Important behavior:

- explicit `slice_plan` input is required for fresh alignment runs
- implicit chapter-by-index fallback has been removed
- reuse `alignment_json_input_path` only when you already trust the saved alignment artifact

## Typical Workflows

### Inspect one book

```python
book = api.extract_book("/path/book.epub", language="ja")
chapters = service.list_book_chapters(book)
preview = service.get_chapter_preview(book, chapters["chapters"][0]["chapter_id"])
structure = service.get_chapter_structure(book, chapters["chapters"][0]["chapter_id"])
```

### Match and align one chapter pair

```python
source = api.extract_book("/path/source.epub", language="ja")
target = api.extract_book("/path/target.epub", language="zh")

matches = service.suggest_chapter_matches(source, target)
candidate = matches["matches"][0]

# Review the candidate with chapter previews or sentence samples before trusting it.
source_chapter_id = candidate["source_chapter_id"]
target_chapter_id = candidate["target_chapter_id"]

aligner = BertalignAdapter(
    model_name="<local-labse-model-path>",
    model_backend="local",
    device="cuda",
    src_lang="ja",
    tgt_lang="zh",
)

alignment = service.align_chapter_pair(
    source,
    target,
    source_chapter_id,
    target_chapter_id,
    granularity="sentence",
    aligner=aligner,
)

report = service.generate_alignment_report(alignment)
```

### Save and reload artifacts

```python
api.save_extraction_json(source, "/tmp/source_extraction.json")
service.export_alignment_json(alignment, "/tmp/alignment.json")
summary = service.read_alignment_artifact("/tmp/alignment.json", view="stats")
```

## Practical Guidance

- Prefer `chapter_id` over numeric indices for local lookup, but not as the only alignment anchor when drift or mixed-content signals exist.
- Use `include_retained=True` for review and structural diagnosis.
- Use `include_retained=False` only when you need a tighter alignable-content view.
- Inspect `get_chapter_structure` or `detect_chapter_anomalies` before aligning noisy chapters.
- Compare `list_book_chapters(...)`, `get_chapter_preview(...)`, and a sample from `sentence_segments` before trusting the first body chapter.
- Use `preview_spine_documents`, `preview_document_raw`, and `detect_mixed_content_chapters` before trusting whole-chapter matches.
- Use `slice_chapter` or split helpers to turn dirty chapters into clean alignment jobs.
- If one `chapter_id` contains multiple body regions or paragraph-index resets, do not force it into `slice_plan`; use a more explicit reviewed workflow.
- Review `inspect_alignment`, `get_unmatched_segments`, and `list_builder_warnings` after each alignment step.
- Export `review.html` and keep it with the alignment artifact for manual review.
- Surface missing model/runtime dependencies explicitly.
- Do not treat heuristic match scores or pair scores as trustworthy semantic confidence.
