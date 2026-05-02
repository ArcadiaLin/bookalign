# Bookalign Production Workflow

## Purpose

Use this guide when the task is no longer "inspect a few chapters" but "produce a reviewable and traceable bilingual EPUB with persisted artifacts".

The production path in this skill is intentionally staged. Do not collapse it into one opaque whole-book alignment step unless the user explicitly accepts the risk.

Important current constraint:

- `slice_plan_json` is required for new production alignment runs
- the previous implicit chapter-by-index fallback has been removed
- if you do not have a trustworthy slice plan yet, stop and inspect instead of running production
- `slice_plan_json` only expresses clean chapter slices; it is not expressive enough for every mixed-chapter case

## Official High-Level Entry Point

Prefer:

```bash
<python-entry> <skill-root>/scripts/build_bilingual_epub.py \
  --source-epub /path/source.epub \
  --target-epub /path/target.epub \
  --artifacts-dir /path/artifacts \
  --source-lang ja \
  --target-lang zh \
  --slice-plan-json /path/slice_plan.json
```

This script persists:

- source extraction JSON
- target extraction JSON
- slice manifest JSON
- alignment JSON
- alignment report JSON
- review HTML
- final bilingual EPUB

The script builds on the existing source-layout EPUB builder instead of replacing it with a new format.

## Recommended Workflow

1. Ask the user to confirm `<python-entry>`, `<skill-root>`, model path, remote-inference policy, and artifacts directory.
2. Run `<python-entry> <skill-root>/scripts/check_environment.py --json`.
3. Extract both books.
4. Inspect chapter lists and spine documents.
5. Compare chapter listings against sampled `sentence_segments` and visible headings.
6. Detect mixed-content chapters and chapter drift.
7. Create a chapter-slice plan only for clean slices.
8. Align each clean slice.
9. Review diagnostics and the generated review HTML.
10. Build the final EPUB.

## Important Service APIs for Production

Use these before alignment:

- `service.preview_spine_documents(extraction)`
- `service.preview_document_raw(extraction, spine_idx)`
- `service.preview_document_rendered(extraction, spine_idx, mode="html"|"markdown")`
- `service.locate_heading_boundaries(extraction, chapter_id)`
- `service.detect_mixed_content_chapters(extraction)`
- `service.slice_chapter(extraction, chapter_id, start_para, end_para, ...)`
- `service.split_chapter_by_heading(extraction, chapter_id, headings=[...])`
- `service.split_chapter_by_predicate(extraction, chapter_id, rule=...)`
- `service.exclude_note_like_segments(extraction, chapter_id, ...)`

Use these after alignment:

- `service.sample_alignment_pairs(alignment)`
- `service.find_alignment_outliers(alignment)`
- `service.group_unmatched_by_region(alignment)`
- `service.compare_alignment_density(alignment)`
- `service.export_review_html(alignment, output_path)`
- `service.build_bilingual_epub_from_alignment(...)`
- `service.build_bilingual_epub_from_alignment_artifact(...)`

## Slice Plan Schema

The production script accepts a JSON file with either `jobs` or `pairs`.

Preferred shape:

```json
{
  "jobs": [
    {
      "job_id": "body-001",
      "granularity": "sentence",
      "source": {
        "chapter_id": "chapter-001",
        "start_para": 0,
        "end_para": 120,
        "exclude_note_like": false,
        "include_retained": true
      },
      "target": {
        "chapter_id": "chapter-004",
        "start_para": 8,
        "end_para": 132,
        "exclude_note_like": true,
        "include_retained": true
      }
    }
  ]
}
```

Field semantics:

- `chapter_id`: chapter id from `service.list_book_chapters(...)`
- `start_para`, `end_para`: inclusive paragraph bounds
- `exclude_note_like`: remove note-like segments from the aligned slice
- `include_retained`: keep non-alignable segments as retained artifacts for builder/review use
- `granularity`: currently prefer `sentence`

Boundary note:

- this schema assumes each job can be described as one `chapter_id` plus monotonic paragraph bounds
- if a single `chapter_id` contains multiple body regions, note blocks, or paragraph-index resets, this schema is not a safe representation
- for those cases, inspect the spine documents first and either split earlier with service helpers or construct a reviewed `AlignmentResult` manually outside the production shortcut

Use `jobs` when you want explicit slice identities and independent ranges. Use `pairs` only for a simpler compatibility form.

Execution rule:

- do not omit the slice plan and expect the script to infer chapter pairing
- whole-book positional pairing is no longer performed by default

## Builder Controls

The production script and service builder wrapper expose:

- `builder_mode`: `simple` or `source_layout`
- `writeback_mode`: `paragraph` or `inline`
- `layout_direction`: `horizontal` or `source`
- `include_note_appendix`: keep or drop retained target notes
- `include_extra_target_appendix`: keep or drop other retained target appendix content

Default production recommendation:

- `builder_mode="source_layout"`
- `writeback_mode="paragraph"`
- `layout_direction="horizontal"`
- Chinese target paragraphs are indented by default with two leading spaces at writeback time

## Artifact Layout

Recommended layout:

```text
artifacts/
├── source_extraction.json
├── target_extraction.json
├── slice_manifest.json
├── alignment.json
├── alignment_report.json
├── review.html
└── bilingual.epub
```

Keep these artifacts. They are useful for:

- resumable work
- human review
- comparing slice strategies
- builder-only reruns without re-running alignment

## Practical Notes

- If chapter numbering drifts, rely on visible headings and paragraph slices, not just chapter labels.
- If a chapter contains mixed body text, notes, or TOC residue, split it before alignment.
- If alignment looks suspicious, inspect outliers and unmatched-region grouping before rebuilding.
- If the final EPUB layout looks wrong, rerun the builder from saved artifacts before recomputing alignment.
- The current chapter matcher is intentionally lightweight; use it to generate suggestions, not as an authoritative execution plan.
