"""Structured service APIs over extraction, alignment, and builder artifacts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
import hashlib
import html
import json
from pathlib import Path
import re

from ebooklib import epub

from alignment_json import load_alignment_result, save_alignment_result
from align.aligner import align_segments
from align.bertalign_adapter import BertalignAdapter
from api import get_chapter_records, list_chapters, load_epub
from epub.cfi import resolve_cfi as resolve_epub_cfi
from epub.extractor import extract_text_from_cfi
from models.types import AlignmentResult, BookExtraction, ChapterInfo, SegmentRecord
from pipeline import extract_sentence_chapters, match_extracted_chapters

_NON_WORD_RE = re.compile(r"[^\w]+", re.UNICODE)
_RULES: dict[str, dict] = {}
_SESSION_RULES: dict[str, set[str]] = {}


def list_book_chapters(extraction: BookExtraction, view: str = "summary") -> dict:
    chapters = [_chapter_payload(extraction, chapter, view=view) for chapter in list_chapters(extraction)]
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "chapters": chapters,
    }


def get_chapter_preview(
    extraction: BookExtraction,
    chapter_id: str | int,
    max_chars: int = 300,
) -> dict:
    chapter = _resolve_chapter(extraction, chapter_id)
    preview = _chapter_text(extraction, chapter, granularity="paragraph", include_retained=True)
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "chapter_id": chapter.chapter_id,
        "preview_text": preview[:max_chars],
        "char_count": len(preview),
    }


def get_chapter_text(
    extraction: BookExtraction,
    chapter_id: str | int,
    granularity: str = "paragraph",
    include_retained: bool = True,
    limit: int | None = None,
    offset: int = 0,
) -> dict:
    chapter = _resolve_chapter(extraction, chapter_id)
    records = get_chapter_records(
        extraction,
        chapter.chapter_id,
        granularity=granularity,
        include_retained=include_retained,
        limit=limit,
        offset=offset,
    )
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "chapter": _chapter_payload(extraction, chapter, view="detail"),
        "granularity": granularity,
        "include_retained": include_retained,
        "offset": offset,
        "limit": limit,
        "segments": [_segment_payload(extraction, record) for record in records],
    }


def get_chapter_structure(extraction: BookExtraction, chapter_id: str | int) -> dict:
    chapter = _resolve_chapter(extraction, chapter_id)
    paragraph_records = get_chapter_records(extraction, chapter.chapter_id, granularity="paragraph", include_retained=True)
    sentence_records = get_chapter_records(extraction, chapter.chapter_id, granularity="sentence", include_retained=True)
    heading_candidates = [
        record.segment.text
        for record in sentence_records
        if record.segment.paratext_kind == "chapter_heading"
    ]
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "chapter_id": chapter.chapter_id,
        "paragraph_count": len(paragraph_records),
        "sentence_count": len(sentence_records),
        "footnote_count": sum(1 for record in paragraph_records if record.segment.is_note_like),
        "heading_candidates": heading_candidates,
        "poetry_line_count": sum(1 for record in paragraph_records if _looks_like_poetry(record.segment.text)),
        "anomaly_segments": [
            _segment_payload(extraction, record)
            for record in paragraph_records
            if _is_anomalous_segment(record.segment.text)
        ],
    }


def search_book_text(
    extraction: BookExtraction,
    query: str,
    scope: str = "all",
) -> dict:
    if scope not in {"all", "chapter", "body"}:
        raise ValueError(f"Unsupported scope: {scope}")
    query_norm = query.strip().casefold()
    if not query_norm:
        return {"book_id": _book_id(extraction), "query": query, "matches": []}

    matches: list[dict] = []
    for record in extraction.paragraph_segments:
        if scope == "body" and record.segment.alignment_role != "align":
            continue
        text_norm = record.segment.text.casefold()
        if query_norm not in text_norm:
            continue
        chapter = _resolve_chapter(extraction, record.chapter_id)
        match = {
            "chapter_id": record.chapter_id,
            "segment_id": _segment_id(extraction, record),
            "granularity": record.granularity,
            "text": record.segment.text,
            "chapter_title": chapter.title or chapter.label,
            "position": text_norm.index(query_norm),
        }
        matches.append(match)

    if scope == "chapter":
        chapter_ids = []
        chapter_matches = []
        for match in matches:
            if match["chapter_id"] in chapter_ids:
                continue
            chapter_ids.append(match["chapter_id"])
            chapter_matches.append(match)
        matches = chapter_matches

    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "query": query,
        "scope": scope,
        "matches": matches,
    }


def list_extracted_chapters(extraction: BookExtraction) -> dict:
    return list_book_chapters(extraction)


def get_extracted_segments(
    extraction: BookExtraction,
    chapter_id: str | int,
    granularity: str = "sentence",
    include_retained: bool = True,
) -> dict:
    return get_chapter_text(
        extraction,
        chapter_id,
        granularity=granularity,
        include_retained=include_retained,
    )


def get_segment(extraction: BookExtraction, segment_id: str) -> dict:
    for record in _iter_records(extraction):
        if _segment_id(extraction, record) == segment_id:
            payload = _segment_payload(extraction, record)
            payload["book_id"] = _book_id(extraction)
            payload["extraction_id"] = _extraction_id(extraction)
            return payload
    raise KeyError(f"Unknown segment_id: {segment_id}")


def get_segment_cfi(extraction: BookExtraction, segment_id: str) -> dict:
    segment = get_segment(extraction, segment_id)
    return {
        "segment_id": segment_id,
        "cfi": segment["cfi"],
        "paragraph_cfi": segment["paragraph_cfi"],
    }


def resolve_cfi(extraction: BookExtraction, cfi: str) -> dict:
    book = _book_from_extraction(extraction)
    resolved = resolve_epub_cfi(cfi, book)
    matched = []
    for record in _iter_records(extraction):
        if record.segment.cfi == cfi or record.segment.paragraph_cfi == cfi:
            matched.append(_segment_payload(extraction, record))
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "cfi": cfi,
        "resolved": _json_safe(resolved),
        "matched_segments": matched,
    }


def locate_text(
    extraction: BookExtraction,
    text_query: str,
    chapter_id: str | None = None,
) -> dict:
    if chapter_id is None:
        return search_book_text(extraction, text_query, scope="all")
    chapter = _resolve_chapter(extraction, chapter_id)
    chapter_result = get_chapter_text(extraction, chapter.chapter_id, granularity="paragraph", include_retained=True)
    matches = []
    needle = text_query.casefold()
    for segment in chapter_result["segments"]:
        pos = segment["text"].casefold().find(needle)
        if pos >= 0:
            matches.append({**segment, "position": pos})
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "query": text_query,
        "chapter_id": chapter.chapter_id,
        "matches": matches,
    }


def extract_text_by_cfi(extraction: BookExtraction, cfi: str) -> dict:
    book = _book_from_extraction(extraction)
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "cfi": cfi,
        "text": extract_text_from_cfi(book, cfi),
    }


def compare_cfi_ranges(extraction: BookExtraction, cfi_a: str, cfi_b: str) -> dict:
    order = {}
    for index, record in enumerate(extraction.paragraph_segments):
        order.setdefault(record.segment.paragraph_cfi or record.segment.cfi, index)
        order.setdefault(record.segment.cfi, index)
    pos_a = order.get(cfi_a)
    pos_b = order.get(cfi_b)
    relation = "unknown"
    if pos_a is not None and pos_b is not None:
        if pos_a == pos_b:
            relation = "same"
        elif pos_a < pos_b:
            relation = "before"
        else:
            relation = "after"
    return {"cfi_a": cfi_a, "cfi_b": cfi_b, "relation": relation}


def suggest_chapter_matches(
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    strategy: str = "heuristic",
) -> dict:
    if strategy != "heuristic":
        raise ValueError(f"Unsupported strategy: {strategy}")
    if source_extraction.source_path and target_extraction.source_path:
        source_chapters = extract_sentence_chapters(_book_from_extraction(source_extraction), language=source_extraction.language)
        target_chapters = extract_sentence_chapters(_book_from_extraction(target_extraction), language=target_extraction.language)
        matches = match_extracted_chapters(source_chapters, target_chapters)
        source_map = {chapter.spine_idx: chapter.chapter_id for chapter in source_extraction.chapters}
        target_map = {chapter.spine_idx: chapter.chapter_id for chapter in target_extraction.chapters}
        suggestions = [
            {
                "source_chapter_id": source_map.get(match.source_chapter.spine_idx, ""),
                "target_chapter_id": target_map.get(match.target_chapter.spine_idx, ""),
                "confidence": round(match.score, 4),
            }
            for match in matches
        ]
    else:
        suggestions = _fallback_chapter_matches(source_extraction, target_extraction)
    return {
        "source_extraction_id": _extraction_id(source_extraction),
        "target_extraction_id": _extraction_id(target_extraction),
        "strategy": strategy,
        "matches": suggestions,
    }


def align_chapter_pair(
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    source_chapter_id: str | int,
    target_chapter_id: str | int,
    granularity: str = "sentence",
    aligner: BertalignAdapter | None = None,
) -> AlignmentResult:
    source_records = _alignable_records(source_extraction, source_chapter_id, granularity)
    target_records = _alignable_records(target_extraction, target_chapter_id, granularity)
    return align_segments(
        [record.segment for record in source_records],
        [record.segment for record in target_records],
        source_lang=source_extraction.language,
        target_lang=target_extraction.language,
        granularity=granularity,
        aligner=aligner,
    )


def align_chapter_ranges(
    source_extraction: BookExtraction,
    target_extraction: BookExtraction,
    source_chapter_ids: Iterable[str | int],
    target_chapter_ids: Iterable[str | int],
    granularity: str = "sentence",
    aligner: BertalignAdapter | None = None,
) -> AlignmentResult:
    source_records = _flatten_alignable_records(source_extraction, source_chapter_ids, granularity)
    target_records = _flatten_alignable_records(target_extraction, target_chapter_ids, granularity)
    return align_segments(
        [record.segment for record in source_records],
        [record.segment for record in target_records],
        source_lang=source_extraction.language,
        target_lang=target_extraction.language,
        granularity=granularity,
        aligner=aligner,
    )


def inspect_alignment(alignment: AlignmentResult) -> dict:
    aligned_pairs = len(alignment.pairs)
    source_unmatched = sum(1 for pair in alignment.pairs if pair.source and not pair.target)
    target_unmatched = sum(1 for pair in alignment.pairs if pair.target and not pair.source)
    return {
        "alignment_id": _alignment_id(alignment),
        "pair_count": aligned_pairs,
        "source_unmatched_pairs": source_unmatched,
        "target_unmatched_pairs": target_unmatched,
        "skip_ratio": round((source_unmatched + target_unmatched) / aligned_pairs, 4) if aligned_pairs else 0.0,
    }


def get_alignment_summary(alignment: AlignmentResult) -> dict:
    source_segments = sum(len(pair.source) for pair in alignment.pairs)
    target_segments = sum(len(pair.target) for pair in alignment.pairs)
    return {
        "alignment_id": _alignment_id(alignment),
        "source_lang": alignment.source_lang,
        "target_lang": alignment.target_lang,
        "granularity": alignment.granularity,
        "pair_count": len(alignment.pairs),
        "source_segment_count": source_segments,
        "target_segment_count": target_segments,
        "retained_source_count": len(alignment.retained_source_segments),
        "retained_target_count": len(alignment.retained_target_segments),
    }


def get_aligned_pairs(
    alignment: AlignmentResult,
    offset: int = 0,
    limit: int = 100,
) -> dict:
    items = alignment.pairs[offset:offset + limit]
    return {
        "alignment_id": _alignment_id(alignment),
        "offset": offset,
        "limit": limit,
        "pairs": [
            {
                "pair_id": f"pair-{offset + index:06d}",
                "score": pair.score,
                "source": [_segment_brief(segment) for segment in pair.source],
                "target": [_segment_brief(segment) for segment in pair.target],
            }
            for index, pair in enumerate(items)
        ],
    }


def get_unmatched_segments(alignment: AlignmentResult, side: str = "source") -> dict:
    if side not in {"source", "target"}:
        raise ValueError(f"Unsupported side: {side}")
    unmatched = []
    for index, pair in enumerate(alignment.pairs):
        segments = pair.source if side == "source" else pair.target
        other = pair.target if side == "source" else pair.source
        if segments and not other:
            unmatched.append(
                {
                    "pair_id": f"pair-{index:06d}",
                    "segments": [_segment_brief(segment) for segment in segments],
                }
            )
    return {"alignment_id": _alignment_id(alignment), "side": side, "items": unmatched}


def get_alignment_block_text(alignment: AlignmentResult, pair_id: str) -> dict:
    index = _pair_index(pair_id)
    pair = alignment.pairs[index]
    return {
        "pair_id": pair_id,
        "source_text": " ".join(segment.text for segment in pair.source),
        "target_text": " ".join(segment.text for segment in pair.target),
        "score": pair.score,
    }


def export_alignment_json(alignment: AlignmentResult, output_path: str | Path) -> dict:
    path = save_alignment_result(alignment, output_path)
    return {
        "artifact_id": _artifact_id(path),
        "path": str(path),
        "alignment_id": _alignment_id(alignment),
    }


def read_alignment_artifact(path: str | Path, view: str = "summary") -> dict:
    alignment = load_alignment_result(path)
    if view == "summary":
        return get_alignment_summary(alignment)
    if view == "pairs":
        return get_aligned_pairs(alignment)
    if view == "stats":
        payload = get_alignment_summary(alignment)
        payload["inspection"] = inspect_alignment(alignment)
        return payload
    raise ValueError(f"Unsupported view: {view}")


def preview_build_plan(
    alignment: AlignmentResult,
    mode: str = "source_layout",
    writeback_mode: str = "paragraph",
) -> dict:
    chapter_counter = Counter(
        segment.chapter_idx
        for pair in alignment.pairs
        for segment in pair.source
    )
    return {
        "alignment_id": _alignment_id(alignment),
        "mode": mode,
        "writeback_mode": writeback_mode,
        "chapter_indices": sorted(chapter_counter),
        "chapter_pair_counts": dict(chapter_counter),
        "warning_count": len(list_builder_warnings(alignment)["warnings"]),
    }


def build_single_chapter_preview(
    alignment: AlignmentResult,
    source_chapter_id: int,
    target_chapter_id: int | None = None,
    mode: str = "html",
) -> dict:
    if mode != "html":
        raise ValueError(f"Unsupported mode: {mode}")
    rows = []
    for pair in alignment.pairs:
        if pair.source and pair.source[0].chapter_idx != source_chapter_id:
            continue
        if target_chapter_id is not None and pair.target and pair.target[0].chapter_idx != target_chapter_id:
            continue
        rows.append(
            "<div class='pair'><p class='source'>{}</p><p class='target'>{}</p></div>".format(
                html.escape(" ".join(segment.text for segment in pair.source) or "[source missing]"),
                html.escape(" ".join(segment.text for segment in pair.target) or "[target missing]"),
            )
        )
    return {"mode": mode, "html": "".join(rows)}


def list_builder_warnings(alignment: AlignmentResult) -> dict:
    warnings = []
    for index, pair in enumerate(alignment.pairs):
        if any(not segment.cfi for segment in pair.source):
            warnings.append({"pair_id": f"pair-{index:06d}", "warning": "missing_source_cfi"})
        if any(segment.has_jump_markup for segment in pair.source + pair.target):
            warnings.append({"pair_id": f"pair-{index:06d}", "warning": "jump_markup_present"})
        if not pair.source or not pair.target:
            warnings.append({"pair_id": f"pair-{index:06d}", "warning": "unmatched_side"})
    return {"alignment_id": _alignment_id(alignment), "warnings": warnings}


def sample_sentences(extraction: BookExtraction, chapter_id: str | None = None, count: int = 10) -> dict:
    records = extraction.sentence_segments
    if chapter_id is not None:
        chapter = _resolve_chapter(extraction, chapter_id)
        records = [record for record in records if record.chapter_id == chapter.chapter_id]
    return {
        "book_id": _book_id(extraction),
        "samples": [_segment_payload(extraction, record) for record in records[:count]],
    }


def guess_language(extraction: BookExtraction, sample_size: int = 20) -> dict:
    samples = " ".join(record.segment.text for record in extraction.sentence_segments[:sample_size])
    guessed = extraction.language
    if re.search(r"[\u3040-\u30ff]", samples):
        guessed = "ja"
    elif re.search(r"[\u4e00-\u9fff]", samples):
        guessed = "zh"
    elif re.search(r"[A-Za-z]", samples):
        guessed = "en"
    return {"book_id": _book_id(extraction), "language": guessed}


def detect_book_features(extraction: BookExtraction) -> dict:
    paragraphs = extraction.paragraph_segments
    return {
        "book_id": _book_id(extraction),
        "has_many_footnotes": sum(1 for record in paragraphs if record.segment.is_note_like) >= 5,
        "has_poetry": any(_looks_like_poetry(record.segment.text) for record in paragraphs),
        "has_vertical_punctuation": any(re.search(r"[︽︾︿﹀﹁﹂﹃﹄]", record.segment.text) for record in paragraphs),
        "has_fragmented_spans": any(len(record.segment.spans) >= 10 for record in paragraphs),
        "has_toc_like_content": any(record.segment.paratext_kind == "toc" for record in paragraphs),
    }


def detect_chapter_anomalies(extraction: BookExtraction) -> dict:
    anomalies = []
    for chapter in extraction.chapters:
        structure = get_chapter_structure(extraction, chapter.chapter_id)
        if structure["footnote_count"] or structure["poetry_line_count"] or structure["anomaly_segments"]:
            anomalies.append(
                {
                    "chapter_id": chapter.chapter_id,
                    "footnote_count": structure["footnote_count"],
                    "poetry_line_count": structure["poetry_line_count"],
                    "anomaly_count": len(structure["anomaly_segments"]),
                }
            )
    return {"book_id": _book_id(extraction), "chapters": anomalies}


def list_rules(rule_type: str | None = None) -> dict:
    items = list(_RULES.values())
    if rule_type is not None:
        items = [rule for rule in items if rule["rule_type"] == rule_type]
    return {"rules": items}


def test_rule(rule_type: str, rule_content: str, sample_input: str) -> dict:
    if rule_type not in _SUPPORTED_RULE_TYPES:
        raise ValueError(f"Unsupported rule_type: {rule_type}")
    matched = re.search(rule_content, sample_input, re.IGNORECASE) is not None
    return {"rule_type": rule_type, "matched": matched}


def register_rule(
    rule_type: str,
    rule_content: str,
    scope: str = "session",
) -> dict:
    if rule_type not in _SUPPORTED_RULE_TYPES:
        raise ValueError(f"Unsupported rule_type: {rule_type}")
    rule_id = _stable_id("rule", rule_type, scope, rule_content)
    _RULES[rule_id] = {
        "rule_id": rule_id,
        "rule_type": rule_type,
        "rule_content": rule_content,
        "scope": scope,
        "enabled": True,
    }
    return _RULES[rule_id]


def enable_rules(session_id: str, rule_ids: Iterable[str]) -> dict:
    enabled = _SESSION_RULES.setdefault(session_id, set())
    for rule_id in rule_ids:
        enabled.add(rule_id)
        if rule_id in _RULES:
            _RULES[rule_id]["enabled"] = True
    return {"session_id": session_id, "rule_ids": sorted(enabled)}


def disable_rule(rule_id: str) -> dict:
    if rule_id not in _RULES:
        raise KeyError(f"Unknown rule_id: {rule_id}")
    _RULES[rule_id]["enabled"] = False
    return _RULES[rule_id]


def explain_rule_hit(extraction: BookExtraction, chapter_id: str, rule_id: str) -> dict:
    if rule_id not in _RULES:
        raise KeyError(f"Unknown rule_id: {rule_id}")
    rule = _RULES[rule_id]
    chapter = get_chapter_text(extraction, chapter_id, granularity="paragraph", include_retained=True)
    hits = []
    for segment in chapter["segments"]:
        if re.search(rule["rule_content"], segment["text"], re.IGNORECASE):
            hits.append(segment)
    return {"rule": rule, "chapter_id": chapter_id, "hits": hits}


def generate_book_report(extraction: BookExtraction) -> dict:
    chapters = list_book_chapters(extraction)["chapters"]
    features = detect_book_features(extraction)
    anomalies = detect_chapter_anomalies(extraction)
    return {"book_id": _book_id(extraction), "chapters": chapters, "features": features, "anomalies": anomalies}


def generate_alignment_report(alignment: AlignmentResult) -> dict:
    return {
        "summary": get_alignment_summary(alignment),
        "inspection": inspect_alignment(alignment),
        "warnings": list_builder_warnings(alignment),
    }


def trace_segment(extraction: BookExtraction, segment_id: str) -> dict:
    segment = get_segment(extraction, segment_id)
    return {
        "segment_id": segment_id,
        "chapter_id": segment["chapter_id"],
        "paragraph_idx": segment["paragraph_idx"],
        "sentence_idx": segment["sentence_idx"],
        "cfi": segment["cfi"],
        "alignment_role": segment["alignment_role"],
        "paratext_kind": segment["paratext_kind"],
    }


def trace_builder_anchor(alignment: AlignmentResult, pair_id: str) -> dict:
    pair = get_alignment_block_text(alignment, pair_id)
    return {
        "pair_id": pair_id,
        "source_text": pair["source_text"],
        "target_text": pair["target_text"],
        "reason": "source segment paragraph_cfi is used as the primary builder anchor",
    }


def list_warnings(alignment: AlignmentResult) -> dict:
    return list_builder_warnings(alignment)


_SUPPORTED_RULE_TYPES = {
    "note_detection",
    "poetry_segmentation",
    "chapter_boundary",
    "paratext_classification",
    "sentence_split_override",
    "inline_cleanup",
}


def _resolve_chapter(extraction: BookExtraction, chapter_id: str | int) -> ChapterInfo:
    for chapter in extraction.chapters:
        if chapter.chapter_id == chapter_id or chapter.chapter_idx == chapter_id or chapter.spine_idx == chapter_id:
            return chapter
    raise KeyError(f"Unknown chapter reference: {chapter_id}")


def _chapter_payload(extraction: BookExtraction, chapter: ChapterInfo, *, view: str) -> dict:
    preview = _chapter_text(extraction, chapter, granularity="paragraph", include_retained=True)
    return {
        "book_id": _book_id(extraction),
        "extraction_id": _extraction_id(extraction),
        "chapter_id": chapter.chapter_id,
        "source_chapter_id": chapter.chapter_id,
        "working_chapter_id": chapter.chapter_id,
        "spine_item_id": f"spine-{chapter.spine_idx:04d}",
        "spine_index": chapter.spine_idx,
        "title": chapter.title,
        "label": chapter.label,
        "kind_guess": _chapter_kind(chapter),
        "preview_text_100": preview[:100],
        "char_count": len(preview),
        "paragraph_count": chapter.paragraph_count,
        "sentence_count_estimate": chapter.sentence_count,
        "view": view,
    }


def _chapter_text(
    extraction: BookExtraction,
    chapter: ChapterInfo,
    *,
    granularity: str,
    include_retained: bool,
) -> str:
    records = get_chapter_records(
        extraction,
        chapter.chapter_id,
        granularity=granularity,
        include_retained=include_retained,
    )
    return "\n".join(record.segment.text for record in records)


def _segment_payload(extraction: BookExtraction, record: SegmentRecord) -> dict:
    return {
        "segment_id": _segment_id(extraction, record),
        "chapter_id": record.chapter_id,
        "chapter_title": record.chapter_title,
        "granularity": record.granularity,
        "text": record.segment.text,
        "cfi": record.segment.cfi,
        "paragraph_cfi": record.segment.paragraph_cfi,
        "paragraph_idx": record.segment.paragraph_idx,
        "sentence_idx": record.segment.sentence_idx,
        "chapter_idx": record.segment.chapter_idx,
        "alignment_role": record.segment.alignment_role,
        "paratext_kind": record.segment.paratext_kind,
        "filter_reason": record.segment.filter_reason,
        "has_jump_markup": record.segment.has_jump_markup,
        "is_note_like": record.segment.is_note_like,
    }


def _segment_brief(segment) -> dict:
    return {
        "text": segment.text,
        "cfi": segment.cfi,
        "chapter_idx": segment.chapter_idx,
        "paragraph_idx": segment.paragraph_idx,
        "sentence_idx": segment.sentence_idx,
    }


def _iter_records(extraction: BookExtraction) -> Iterable[SegmentRecord]:
    yield from extraction.sentence_segments
    yield from extraction.paragraph_segments


def _book_from_extraction(extraction: BookExtraction) -> epub.EpubBook:
    if not extraction.source_path:
        raise ValueError("Extraction does not have source_path; CFI and chapter matching APIs need it")
    return load_epub(extraction.source_path)


def _stable_id(prefix: str, *parts) -> str:
    raw = "||".join(str(part) for part in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _slugify(text: str) -> str:
    return _NON_WORD_RE.sub("-", text.strip().casefold()).strip("-")


def _book_id(extraction: BookExtraction) -> str:
    source = extraction.source_path or extraction.language or "book"
    label = _slugify(Path(source).stem) or "book"
    return f"{label}-{_stable_id('book', source)}"


def _extraction_id(extraction: BookExtraction) -> str:
    return _stable_id(
        "extract",
        _book_id(extraction),
        extraction.language,
        extraction.extract_mode,
        extraction.default_granularity,
    )


def _segment_id(extraction: BookExtraction, record: SegmentRecord) -> str:
    return _stable_id(
        "seg",
        _extraction_id(extraction),
        record.chapter_id,
        record.granularity,
        record.segment.paragraph_idx,
        record.segment.sentence_idx,
        record.segment.cfi,
        record.segment.text,
    )


def _alignment_id(alignment: AlignmentResult) -> str:
    return _stable_id(
        "align",
        alignment.source_lang,
        alignment.target_lang,
        alignment.granularity,
        len(alignment.pairs),
        sum(len(pair.source) + len(pair.target) for pair in alignment.pairs),
    )


def _artifact_id(path: str | Path) -> str:
    path = Path(path)
    return _stable_id("artifact", path.resolve(), path.stat().st_size if path.exists() else 0)


def _pair_index(pair_id: str) -> int:
    if not pair_id.startswith("pair-"):
        raise KeyError(f"Unsupported pair_id: {pair_id}")
    return int(pair_id.split("-", 1)[1])


def _chapter_kind(chapter: ChapterInfo) -> str:
    label = (chapter.label or chapter.title).casefold()
    if chapter.is_paratext:
        if "toc" in label or "目次" in label or "目录" in label:
            return "toc"
        if "preface" in label or "前言" in label:
            return "preface"
        if "note" in label or "注" in label:
            return "note"
        if "appendix" in label or "附录" in label:
            return "appendix"
        return "unknown"
    return "body"


def _looks_like_poetry(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 2:
        return True
    return "<br" in text and len(text) <= 120


def _is_anomalous_segment(text: str) -> bool:
    stripped = text.strip()
    return len(stripped) < 2 or len(stripped) > 800


def _alignable_records(
    extraction: BookExtraction,
    chapter_id: str | int,
    granularity: str,
) -> list[SegmentRecord]:
    return [
        record
        for record in get_chapter_records(extraction, chapter_id, granularity=granularity, include_retained=False)
        if record.segment.alignment_role == "align"
    ]


def _flatten_alignable_records(
    extraction: BookExtraction,
    chapter_ids: Iterable[str | int],
    granularity: str,
) -> list[SegmentRecord]:
    records = []
    for chapter_id in chapter_ids:
        records.extend(_alignable_records(extraction, chapter_id, granularity))
    return records


def _fallback_chapter_matches(source_extraction: BookExtraction, target_extraction: BookExtraction) -> list[dict]:
    count = min(len(source_extraction.chapters), len(target_extraction.chapters))
    matches = []
    for index in range(count):
        source_chapter = source_extraction.chapters[index]
        target_chapter = target_extraction.chapters[index]
        matches.append(
            {
                "source_chapter_id": source_chapter.chapter_id,
                "target_chapter_id": target_chapter.chapter_id,
                "confidence": 1.0 if source_chapter.label == target_chapter.label else 0.5,
            }
        )
    return matches


def _json_safe(value):
    if value is None:
        return None
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))
