# Extraction Refactor

## Summary

This refactor upgrades EPUB extraction from a skip-filter model into a policy-driven model.

- Strategy layer: `bookalign/epub/tag_filters.py`
- Production extraction path: `bookalign/epub/extractor.py`
- Debug/report path: `bookalign/epub/debug_report.py`

The production path is still centered on:

- readable `text`
- `cfi`
- `chapter_idx`
- `paragraph_idx`
- optional `sentence_idx`
- `raw_html`

XPath remains available for diagnostics and tests, but the runtime extraction and roundtrip logic do not depend on XPath to reconstruct text.

## Policy Layer

`tag_filters.py` now exposes:

- `ExtractAction`
- `ElementPolicy`
- `match_element_policy(element, config)`
- `get_extract_action(element, config)`

The extractor only asks for the effective action and avoids scattering tag-specific rules.

Key built-in policies:

- `ruby -> KEEP_CHILDREN_ONLY`
- `rt -> SKIP_ENTIRE`
- `rp -> SKIP_ENTIRE`
- `br -> INLINE_BREAK`
- `aside[epub:type=footnote] -> SKIP_ENTIRE`
- `a.noteref` / `a[epub:type=noteref] -> SKIP_ENTIRE`
- `span.super -> SKIP_ENTIRE`
- `section/article/header/footer -> STRUCTURAL_CONTAINER`
- `p/div/li/blockquote/... -> BLOCK_BREAK`
- `strong/em/b/i -> KEEP_NORMAL`
- `svg/math/img -> SKIP_ENTIRE`

Legacy configuration fields such as `skip_tags`, `skip_classes`, `skip_rules`, `block_tags`, and `include_child_text_tags` are still accepted and converted into policies in `TagFilterConfig.__post_init__`.

## Extractor Changes

`extractor.py` now treats element behavior through `ExtractAction`.

Main behavior:

- `SKIP_ENTIRE`: skip node and descendants, keep parent tail when applicable
- `KEEP_NORMAL`: keep direct text, recurse into readable inline descendants, keep tail
- `KEEP_CHILDREN_ONLY`: recurse as readable content without making the node itself special in segment logic
- `KEEP_DIRECT_TEXT_ONLY`: keep only direct text, skip descendant text, keep tail
- `INLINE_BREAK`: emit a synthetic lightweight separator
- `BLOCK_BREAK`: segment candidate
- `STRUCTURAL_CONTAINER`: not a segment candidate; continue handling child blocks separately

The refactor also tightened these areas:

- ruby base text is preserved while `rt/rp` are removed
- superscript note markers and noteref links are suppressed through policy rules
- sentence segments reuse the same normalized paragraph spans as paragraph extraction
- `extract_text_from_cfi()` uses the same readable-text definition as the extractor
- CFI roundtrip mismatches caused by ruby anchor placement were fixed by separating child-anchor and tail-anchor mapping

## Production vs Debug Layers

Production path:

- `extract_segments()`
- `extract_text_from_cfi()`
- `Segment`

Debug/test path:

- `collect_debug_spans()`
- `DebugSpan`
- `generate_report()` / `python -m bookalign.epub.debug_report`

Debug output includes:

- XPath
- matched action
- matched policy name
- text preview

This keeps audit metadata out of the core segment model while still making test runs inspectable.

## Test Coverage

Updated tests in `tests/test_extractor.py` cover:

- policy matching for ruby / rt / br / footnote / structural containers
- action-driven span extraction
- custom `KEEP_DIRECT_TEXT_ONLY` policy behavior
- debug span emission
- multilingual integration checks on real EPUBs
- CFI roundtrip equality with extracted paragraph text
- Markdown report generation

Command:

```bash
python -m pytest tests/test_splitter.py tests/test_extractor.py -q
```

Observed result during this run:

```text
12 passed in 97.29s
```

## Markdown Audit Entry Point

Example:

```bash
python -m bookalign.epub.debug_report \
  --book kinkaku.epub \
  --seed 20260315 \
  --sample-count 4 \
  --test-type ruby \
  --granularity sentence \
  --language ja \
  --debug \
  --output tests/artifacts/report_kinkaku_ruby.md
```

Supported knobs:

- `--book`
- `--seed`
- `--sample-count`
- `--test-type`
- `--granularity`
- `--language`
- `--debug`
- `--output`

## Current Status

Fixed:

- policy/action abstraction replacing binary skip checks
- ruby/rt/rp handling in extractor and roundtrip
- suppression of `span.super`, `a.noteref`, footnote containers, toc nodes
- sentence extraction reuse of paragraph span boundaries
- debug report generation

Mitigated:

- `br` handling now produces a light separator, which is safer for prose but still heuristic for poetry-heavy EPUBs
- structural container over-segmentation is reduced through explicit `STRUCTURAL_CONTAINER`

Remaining boundaries:

- `INLINE_BREAK` is still a generic separator and may not be ideal for verse/layout-heavy books
- report sampling is heuristic; rare edge-case generator patterns may require custom test-type filters
- sentence alignment still starts from splitter output and then maps back to span ranges, so extremely irregular punctuation can still be brittle
