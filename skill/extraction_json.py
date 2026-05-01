"""Serialization helpers for single-book extraction payloads."""

from __future__ import annotations

import json
from pathlib import Path

from models.types import BookExtraction, ChapterInfo, JumpFragment, Segment, SegmentRecord, TextSpan


def save_extraction_result(extraction: BookExtraction, path: str | Path) -> Path:
    payload = {
        'language': extraction.language,
        'extract_mode': extraction.extract_mode,
        'default_granularity': extraction.default_granularity,
        'source_path': extraction.source_path,
        'chapters': [_chapter_to_dict(chapter) for chapter in extraction.chapters],
        'sentence_segments': [_segment_record_to_dict(record) for record in extraction.sentence_segments],
        'paragraph_segments': [_segment_record_to_dict(record) for record in extraction.paragraph_segments],
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return output_path


def load_extraction_result(path: str | Path) -> BookExtraction:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    return BookExtraction(
        language=payload.get('language', ''),
        extract_mode=payload.get('extract_mode', 'filtered_preserve'),
        default_granularity=payload.get('default_granularity', 'sentence'),
        source_path=payload.get('source_path', ''),
        chapters=[_chapter_from_dict(item) for item in payload.get('chapters', [])],
        sentence_segments=[_segment_record_from_dict(item) for item in payload.get('sentence_segments', [])],
        paragraph_segments=[_segment_record_from_dict(item) for item in payload.get('paragraph_segments', [])],
    )


def _chapter_to_dict(chapter: ChapterInfo) -> dict:
    return {
        'chapter_id': chapter.chapter_id,
        'chapter_idx': chapter.chapter_idx,
        'spine_idx': chapter.spine_idx,
        'title': chapter.title,
        'label': chapter.label,
        'is_paratext': chapter.is_paratext,
        'sentence_count': chapter.sentence_count,
        'paragraph_count': chapter.paragraph_count,
        'alignment_sentence_count': chapter.alignment_sentence_count,
        'alignment_paragraph_count': chapter.alignment_paragraph_count,
    }


def _chapter_from_dict(payload: dict) -> ChapterInfo:
    return ChapterInfo(
        chapter_id=payload.get('chapter_id', ''),
        chapter_idx=int(payload.get('chapter_idx', 0)),
        spine_idx=int(payload.get('spine_idx', 0)),
        title=payload.get('title', ''),
        label=payload.get('label', ''),
        is_paratext=bool(payload.get('is_paratext', False)),
        sentence_count=int(payload.get('sentence_count', 0)),
        paragraph_count=int(payload.get('paragraph_count', 0)),
        alignment_sentence_count=int(payload.get('alignment_sentence_count', 0)),
        alignment_paragraph_count=int(payload.get('alignment_paragraph_count', 0)),
    )


def _segment_record_to_dict(record: SegmentRecord) -> dict:
    return {
        'chapter_id': record.chapter_id,
        'chapter_title': record.chapter_title,
        'granularity': record.granularity,
        'segment': _segment_to_dict(record.segment),
    }


def _segment_record_from_dict(payload: dict) -> SegmentRecord:
    return SegmentRecord(
        segment=_segment_from_dict(payload.get('segment', {})),
        chapter_id=payload.get('chapter_id', ''),
        chapter_title=payload.get('chapter_title', ''),
        granularity=payload.get('granularity', 'sentence'),
    )


def _segment_to_dict(segment: Segment) -> dict:
    return {
        'text': segment.text,
        'cfi': segment.cfi,
        'chapter_idx': segment.chapter_idx,
        'paragraph_idx': segment.paragraph_idx,
        'sentence_idx': segment.sentence_idx,
        'paragraph_cfi': segment.paragraph_cfi,
        'text_start': segment.text_start,
        'text_end': segment.text_end,
        'raw_html': segment.raw_html,
        'element_xpath': segment.element_xpath,
        'has_jump_markup': segment.has_jump_markup,
        'is_note_like': segment.is_note_like,
        'alignment_role': segment.alignment_role,
        'paratext_kind': segment.paratext_kind,
        'filter_reason': segment.filter_reason,
        'jump_fragments': [_jump_fragment_to_dict(fragment) for fragment in segment.jump_fragments],
        'spans': [_span_to_dict(span) for span in segment.spans],
    }


def _segment_from_dict(payload: dict) -> Segment:
    return Segment(
        text=payload.get('text', ''),
        cfi=payload.get('cfi', ''),
        chapter_idx=int(payload.get('chapter_idx', 0)),
        paragraph_idx=int(payload.get('paragraph_idx', 0)),
        sentence_idx=payload.get('sentence_idx'),
        paragraph_cfi=payload.get('paragraph_cfi', ''),
        text_start=payload.get('text_start'),
        text_end=payload.get('text_end'),
        raw_html=payload.get('raw_html', ''),
        element_xpath=payload.get('element_xpath', ''),
        has_jump_markup=bool(payload.get('has_jump_markup', False)),
        is_note_like=bool(payload.get('is_note_like', False)),
        alignment_role=payload.get('alignment_role', 'align'),
        paratext_kind=payload.get('paratext_kind', 'body'),
        filter_reason=payload.get('filter_reason', ''),
        jump_fragments=[_jump_fragment_from_dict(item) for item in payload.get('jump_fragments', [])],
        spans=[_span_from_dict(item) for item in payload.get('spans', [])],
    )


def _jump_fragment_to_dict(fragment: JumpFragment) -> dict:
    return {
        'kind': fragment.kind,
        'text': fragment.text,
        'start': fragment.start,
        'end': fragment.end,
        'href': fragment.href,
        'anchor_id': fragment.anchor_id,
    }


def _jump_fragment_from_dict(payload: dict) -> JumpFragment:
    return JumpFragment(
        kind=payload.get('kind', ''),
        text=payload.get('text', ''),
        start=payload.get('start'),
        end=payload.get('end'),
        href=payload.get('href', ''),
        anchor_id=payload.get('anchor_id', ''),
    )


def _span_to_dict(span: TextSpan) -> dict:
    return {
        'text': span.text,
        'xpath': span.xpath,
        'text_node_index': span.text_node_index,
        'char_offset': span.char_offset,
        'source_kind': span.source_kind,
        'cfi_text_node_index': span.cfi_text_node_index,
        'cfi_exact': span.cfi_exact,
    }


def _span_from_dict(payload: dict) -> TextSpan:
    return TextSpan(
        text=payload.get('text', ''),
        xpath=payload.get('xpath', ''),
        text_node_index=int(payload.get('text_node_index', 0)),
        char_offset=int(payload.get('char_offset', 0)),
        source_kind=payload.get('source_kind', 'text'),
        cfi_text_node_index=payload.get('cfi_text_node_index'),
        cfi_exact=bool(payload.get('cfi_exact', False)),
    )
