"""High-level production workflow helpers for bilingual EPUB output."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from align.aligner import align_segments
from alignment_json import load_alignment_result, save_alignment_result
from api import extract_book, load_epub, save_extraction_json
from epub.builder import build_bilingual_epub, build_bilingual_epub_on_source_layout
from models.types import AlignmentResult, BookExtraction, Segment, SegmentRecord


def build_bilingual_epub_from_alignment(
    *,
    alignment: AlignmentResult,
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    output_path: str | Path,
    builder_mode: str = "source_layout",
    writeback_mode: str = "paragraph",
    layout_direction: str = "horizontal",
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    include_note_appendix: bool = True,
    include_extra_target_appendix: bool = True,
) -> Path:
    source_book = _book_from_extraction(source_extraction)
    target_book = _book_from_extraction(target_extraction)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if builder_mode == "simple":
        build_bilingual_epub(alignment, source_book, target_book, output_path)
        return output_path
    if builder_mode == "source_layout":
        build_bilingual_epub_on_source_layout(
            alignment,
            source_book,
            target_book,
            output_path,
            writeback_mode=writeback_mode,
            layout_direction=layout_direction,
            emit_translation_metadata=emit_translation_metadata,
            normalize_vertical_punctuation=normalize_vertical_punctuation,
            extract_mode=source_extraction.extract_mode,
            include_note_appendix=include_note_appendix,
            include_extra_target_appendix=include_extra_target_appendix,
        )
        return output_path
    raise ValueError(f"Unsupported builder_mode: {builder_mode}")


def build_bilingual_epub_from_alignment_json(
    *,
    alignment_json_path: str | Path,
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    output_path: str | Path,
    builder_mode: str = "source_layout",
    writeback_mode: str = "paragraph",
    layout_direction: str = "horizontal",
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    include_note_appendix: bool = True,
    include_extra_target_appendix: bool = True,
) -> Path:
    alignment = load_alignment_result(alignment_json_path)
    return build_bilingual_epub_from_alignment(
        alignment=alignment,
        source_extraction=source_extraction,
        target_extraction=target_extraction,
        output_path=output_path,
        builder_mode=builder_mode,
        writeback_mode=writeback_mode,
        layout_direction=layout_direction,
        emit_translation_metadata=emit_translation_metadata,
        normalize_vertical_punctuation=normalize_vertical_punctuation,
        include_note_appendix=include_note_appendix,
        include_extra_target_appendix=include_extra_target_appendix,
    )


def run_bilingual_production(
    *,
    source_epub_path: str | Path,
    target_epub_path: str | Path,
    artifacts_dir: str | Path,
    source_lang: str,
    target_lang: str,
    aligner,
    slice_plan: dict | None = None,
    alignment_json_input_path: str | Path | None = None,
    builder_mode: str = "source_layout",
    writeback_mode: str = "paragraph",
    layout_direction: str = "horizontal",
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    include_note_appendix: bool = True,
    include_extra_target_appendix: bool = True,
) -> dict[str, object]:
    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    source_extraction = extract_book(source_epub_path, language=source_lang)
    target_extraction = extract_book(target_epub_path, language=target_lang)
    source_extraction_path = save_extraction_json(source_extraction, artifacts_dir / "source_extraction.json")
    target_extraction_path = save_extraction_json(target_extraction, artifacts_dir / "target_extraction.json")

    if alignment_json_input_path is not None:
        alignment = load_alignment_result(alignment_json_input_path)
        slice_manifest = {"mode": "alignment_json_input", "path": str(Path(alignment_json_input_path))}
    else:
        alignment, slice_manifest = align_from_slice_plan(
            source_extraction=source_extraction,
            target_extraction=target_extraction,
            slice_plan=slice_plan,
            aligner=aligner,
        )

    alignment_path = save_alignment_result(alignment, artifacts_dir / "alignment.json")
    (artifacts_dir / "slice_manifest.json").write_text(
        json.dumps(slice_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output_epub_path = artifacts_dir / "bilingual.epub"
    build_bilingual_epub_from_alignment(
        alignment=alignment,
        source_extraction=source_extraction,
        target_extraction=target_extraction,
        output_path=output_epub_path,
        builder_mode=builder_mode,
        writeback_mode=writeback_mode,
        layout_direction=layout_direction,
        emit_translation_metadata=emit_translation_metadata,
        normalize_vertical_punctuation=normalize_vertical_punctuation,
        include_note_appendix=include_note_appendix,
        include_extra_target_appendix=include_extra_target_appendix,
    )
    return {
        "artifacts_dir": str(artifacts_dir),
        "source_extraction_json": str(source_extraction_path),
        "target_extraction_json": str(target_extraction_path),
        "slice_manifest_json": str(artifacts_dir / "slice_manifest.json"),
        "alignment_json": str(alignment_path),
        "output_epub": str(output_epub_path),
    }


def align_from_slice_plan(
    *,
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    slice_plan: dict | None,
    aligner,
) -> tuple[AlignmentResult, dict[str, object]]:
    jobs = _normalize_jobs(source_extraction, target_extraction, slice_plan)
    combined = AlignmentResult(
        pairs=[],
        source_lang=source_extraction.language,
        target_lang=target_extraction.language,
        granularity="sentence",
    )
    manifest_jobs = []
    for job in jobs:
        granularity = job.get("granularity", "sentence")
        source_records = _select_records(source_extraction, job["source"], granularity=granularity)
        target_records = _select_records(target_extraction, job["target"], granularity=granularity)
        result = align_segments(
            [record.segment for record in source_records["alignable"]],
            [record.segment for record in target_records["alignable"]],
            source_lang=source_extraction.language,
            target_lang=target_extraction.language,
            granularity=granularity,
            aligner=aligner,
        )
        combined.pairs.extend(result.pairs)
        combined.retained_source_segments.extend(record.segment for record in source_records["retained"])
        combined.retained_target_segments.extend(record.segment for record in target_records["retained"])
        manifest_jobs.append(
            {
                "job_id": job["job_id"],
                "granularity": granularity,
                "source": _materialize_slice_manifest(job["source"], source_records),
                "target": _materialize_slice_manifest(job["target"], target_records),
                "pair_count": len(result.pairs),
            }
        )
    return combined, {"mode": "slice_plan", "jobs": manifest_jobs}


def write_json(path: str | Path, payload: dict | list) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _materialize_slice_manifest(spec: dict, selected: dict[str, list[SegmentRecord]]) -> dict[str, object]:
    payload = dict(spec)
    payload["alignable_count"] = len(selected["alignable"])
    payload["retained_count"] = len(selected["retained"])
    payload["text_preview"] = " ".join(record.segment.text for record in selected["alignable"][:3])[:240]
    return payload


def _normalize_jobs(
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    slice_plan: dict | None,
) -> list[dict]:
    if not slice_plan:
        raise ValueError(
            "slice_plan is required for production alignment; "
            "implicit chapter-by-index pairing has been removed"
        )

    if "jobs" in slice_plan:
        return [
            {
                "job_id": job.get("job_id", f"job-{index + 1:03d}"),
                "source": job["source"],
                "target": job["target"],
                "granularity": job.get("granularity", "sentence"),
            }
            for index, job in enumerate(slice_plan["jobs"])
        ]

    if "pairs" in slice_plan:
        return [
            {
                "job_id": pair.get("job_id", f"pair-{index + 1:03d}"),
                "source": pair["source"],
                "target": pair["target"],
                "granularity": pair.get("granularity", "sentence"),
            }
            for index, pair in enumerate(slice_plan["pairs"])
        ]
    raise ValueError("slice_plan must contain either 'jobs' or 'pairs'")


def _select_records(
    extraction: BookExtraction,
    spec: dict,
    *,
    granularity: str,
) -> dict[str, list[SegmentRecord]]:
    chapter_ref = spec["chapter_id"]
    start_para = spec.get("start_para")
    end_para = spec.get("end_para")
    exclude_note_like = bool(spec.get("exclude_note_like", False))
    include_retained = bool(spec.get("include_retained", True))

    records = extraction.sentence_segments if granularity == "sentence" else extraction.paragraph_segments
    chapter_records = [record for record in records if record.chapter_id == chapter_ref]
    if start_para is not None:
        chapter_records = [record for record in chapter_records if record.segment.paragraph_idx >= start_para]
    if end_para is not None:
        chapter_records = [record for record in chapter_records if record.segment.paragraph_idx <= end_para]

    alignable = []
    retained = []
    for record in chapter_records:
        if exclude_note_like and record.segment.is_note_like:
            retained.append(record)
            continue
        if record.segment.alignment_role == "align":
            alignable.append(record)
        elif include_retained:
            retained.append(record)
    return {"alignable": alignable, "retained": retained}


def _book_from_extraction(extraction: BookExtraction):
    if not extraction.source_path:
        raise ValueError("Extraction does not have source_path; builder APIs require source EPUB paths")
    return load_epub(extraction.source_path)
