# Bookalign LaBSE Workflow Reference

## Table of Contents

- Purpose and capability boundaries
- Standard workflow
- Environment and backend checks
- Review patterns
- Rule APIs
- Failure handling

## Purpose and capability boundaries

Use this document when the task needs the full review-first workflow, backend choice rules, or safe failure handling.

Bookalign is good at:

- reading EPUBs through a stable Python API
- producing structured extraction objects for one book
- exposing chapter previews, chapter text, chapter structure, and search
- suggesting chapter matches between source and target books
- running Bertalign on local chapter pairs or short chapter ranges
- returning structured alignment summaries and diagnostics
- resolving CFI back to extracted segments
- providing lightweight rule registration and rule-hit explanation

Bookalign is not a full workflow engine:

- it does not manage persistent sessions or a durable artifact store
- it does not provide a full human-editable alignment lifecycle
- rules are not automatically wired into extraction execution
- pair scores are not calibrated semantic confidence scores
- whole-book automatic alignment should not be treated as safe by default

Bookalign chapter metadata also has an important boundary:

- `chapter_id` is a useful lookup key inside one extracted view
- it is not a guaranteed stable anchor across previews, heading text, and sentence-level record ownership

## Standard workflow

Follow this order unless the user explicitly asks for a narrower task:

1. Ask the user to confirm `<skill-root>`, `<python-entry>`, local model path, remote-inference policy, and artifact location.
2. Check runtime readiness with `<python-entry> <skill-root>/scripts/check_environment.py`.
3. Extract one or two books with `api.extract_book(...)`.
4. Browse chapters and anomaly signals before alignment.
5. Run a chapter-consistency self-check against sentence-level records.
6. Suggest chapter matches.
7. Align one chapter pair or a small chapter range at a time.
8. Inspect warnings, unmatched content, and suspicious pairs.
9. Call `service.review_unaligned_segments(...)` to inspect every remaining one-sided block before deciding whether to continue.
10. Iterate.

### Import pattern

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

### Inspect before alignment

Prefer these APIs during review:

- `service.list_book_chapters(extraction)`
- `service.get_chapter_preview(extraction, chapter_id)`
- `service.get_chapter_structure(extraction, chapter_id)`
- `service.search_book_text(extraction, query)`
- `service.detect_book_features(extraction)`
- `service.detect_chapter_anomalies(extraction)`

Review for:

- table-of-contents anomalies
- heavy footnote density
- suspiciously short or long chapters
- chapters dominated by retained paratext
- chapter boundaries that do not line up with expected structure

### Chapter-consistency self-check

Run this before trusting chapter matching:

1. Call `service.list_book_chapters(...)`.
2. Inspect visible openings with `service.get_chapter_preview(...)`.
3. Confirm heading candidates with `service.get_chapter_structure(...)`.
4. Compare those results against a direct sample from `extraction.sentence_segments` or `service.sample_sentences(...)`.

You are checking whether:

- the chapter preview and the first sentence records describe the same body section
- notes, chronology, commentary, or preface residue were merged into the same visible chapter bucket
- paragraph or section indexing appears to reset inside one `chapter_id`

If these views disagree, stop and inspect spine documents or raw text before aligning.

### Detect chapter-number drift explicitly

Some EPUBs expose chapter ids that are offset from the visible chapter numbering because contents, chronology, prefaces, translator notes, or split front matter occupy earlier spine entries.

Use this quick drift check before trusting automatic chapter suggestions:

1. Call `service.list_book_chapters(...)` on both books.
2. Inspect the first few candidate body chapters with `service.get_chapter_preview(...)`.
3. Compare the visible heading text inside the preview with the chapter id.
4. Confirm suspicious cases with `service.get_chapter_structure(...)`.

Common drift patterns:

- `chapter-iii` contains visible heading text `CHAPTER I`
- a translated chapter id like `第三章` contains visible heading text `第二章`
- `kind_guess` remains `unknown` even when the chapter is clearly contents, chronology, or preface-like material

If you see this pattern, do not align the first suggested match immediately. Inspect adjacent chapter ids on both sides and choose the first pair whose visible body text actually lines up.

### Suggest matches, then align locally

Use:

```python
matches = service.suggest_chapter_matches(source, target)
```

Treat the result as a suggestion, not as proof.

Start local alignment with:

```python
alignment = service.align_chapter_pair(
    source,
    target,
    source_chapter_id,
    target_chapter_id,
    aligner=aligner,
)
```

Do not start with the whole book.

## Environment and backend checks

Run `scripts/check_environment.py` before choosing a backend. The script reports core extraction dependencies, optional alignment dependencies, Torch/CUDA state, `HF_TOKEN` presence, and a conservative backend recommendation.

### GPU check

Recommended Python-side check:

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
```

If `torch` is unavailable, assume CPU and surface that limitation clearly.

### Hugging Face token check

```python
import os

hf_token = os.environ.get("HF_TOKEN")
```

Use Hugging Face inference only when `HF_TOKEN` exists and the user accepts remote inference.

### Backend choice

Use local backend when:

- local model dependencies are installed
- GPU is available or CPU use is acceptable
- local model loading is preferred

When `scripts/check_environment.py` reports `recommended_backend` as `local_cuda` or `local_cpu`, prefer the explicit `recommended_model_name` path instead of a registry/model-hub identifier. That should be a user-confirmed local path such as `<local-labse-model-path>`.

Interpret the environment report this way:

- `local_cuda`: local dependencies, local model path, and CUDA are ready
- `local_cpu`: local dependencies and local model path are ready, but CUDA is unavailable
- `hf_inference`: remote inference is the best ready path
- `local_model_missing`: local dependencies exist, but no ready local SentenceTransformer path was found
- `inspection_only`: only extraction/inspection workflows are safely ready

Use Hugging Face inference when:

- local SentenceTransformer dependencies are unavailable
- local model download is undesirable
- `HF_TOKEN` is configured

If both routes are unavailable, stop before alignment and tell the user exactly which prerequisite is missing.

If `HF_ENDPOINT`, `HTTP_PROXY`, or `HTTPS_PROXY` are set, mention them during diagnostics. They can affect initial model resolution even when the intended backend is local.

## Review patterns

### Alignment review

Use these APIs after each local alignment:

- `service.get_alignment_summary(alignment)`
- `service.get_aligned_pairs(alignment, limit=100)`
- `service.get_unmatched_segments(alignment, side="source")`
- `service.get_unmatched_segments(alignment, side="target")`
- `service.review_unaligned_segments(alignment)`
- `service.get_alignment_block_text(alignment, pair_id)`
- `service.list_builder_warnings(alignment)`
- `service.build_single_chapter_preview(alignment, source_chapter_id, mode="html")`

Treat the `score` field from `service.get_aligned_pairs(...)` as a placeholder transport value, not as a model confidence score. Real review should focus on text plausibility, unmatched segments, and warning patterns.

Prefer `service.review_unaligned_segments(...)` when the agent needs one pass that shows all currently unaligned source-only and target-only content, with both per-pair details and merged unmatched regions. This is the recommended interface for deciding whether to:

- manually align a leftover block
- reslice the chapter
- run another local alignment pass
- intentionally leave a region unmatched

### Suspicious pair loop

If a pair looks wrong:

1. Read it with `service.get_alignment_block_text(...)`.
2. Look up the chapter text with `service.get_chapter_text(...)`.
3. Search nearby content with `service.locate_text(...)`.
4. Resolve exact positions with `service.resolve_cfi(...)` or `service.extract_text_by_cfi(...)`.

This library does not provide a trustworthy semantic confidence score per pair. Use explicit inspection.

### Builder boundary

Builder functions still exist in `epub.builder`, but the preferred workflow is:

- inspect first
- align locally
- preview locally

Do not assume it is safe to build a whole bilingual EPUB from an unreviewed alignment result.

## Rule APIs

Use:

- `service.register_rule(rule_type, rule_content, scope="project")`
- `service.test_rule(rule_type, rule_content, sample_input)`
- `service.list_rules(rule_type=None)`
- `service.explain_rule_hit(extraction, chapter_id, rule_id)`

Supported rule types:

- `note_detection`
- `poetry_segmentation`
- `chapter_boundary`
- `paratext_classification`
- `sentence_split_override`
- `inline_cleanup`

Important boundary: rules are registration, validation, and explanation helpers. They are not automatically applied during extraction or alignment.

## Failure handling

### Missing GPU

If no GPU is available:

- prefer `device="cpu"`
- or prefer `model_backend="hf_inference"` if `HF_TOKEN` exists

### Missing HF token

If the chosen backend is `hf_inference` and `HF_TOKEN` is missing:

- treat this as a hard configuration error
- recommend setting `HF_TOKEN`
- or switching back to `model_backend="local"`

### Missing local dependencies

If local backend fails because `sentence-transformers`, `torch`, or related dependencies are missing:

- recommend switching to `hf_inference`
- or installing the local dependencies

### No usable model path

If local alignment is unavailable and Hugging Face inference is unavailable, do not silently continue into alignment. Explain which access path is missing and ask the user how to proceed.

### EPUB extraction failure

If `api.extract_book(...)` fails:

- verify the EPUB path
- verify the EPUB is parseable
- stop before alignment

### Weak alignment quality

Common signals:

- many unmatched segments
- many empty-sided pairs
- chapter preview mismatch
- large builder warning counts
- obviously wrong chapter pairing

Use:

- `service.get_alignment_summary(...)`
- `service.get_unmatched_segments(...)`
- `service.review_unaligned_segments(...)`
- `service.list_builder_warnings(...)`
- `service.build_single_chapter_preview(...)`
