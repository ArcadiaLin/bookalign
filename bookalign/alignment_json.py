"""Serialize and load alignment results for repeatable builder tests."""

from __future__ import annotations

import json
from pathlib import Path

from bookalign.models.types import AlignmentResult, AlignedPair, Segment, TextSpan


def save_alignment_result(alignment: AlignmentResult, path: str | Path) -> Path:
    payload = {
        'source_lang': alignment.source_lang,
        'target_lang': alignment.target_lang,
        'granularity': alignment.granularity,
        'pairs': [_pair_to_dict(pair) for pair in alignment.pairs],
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    return output_path


def load_alignment_result(path: str | Path) -> AlignmentResult:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    return AlignmentResult(
        pairs=[_pair_from_dict(item) for item in payload.get('pairs', [])],
        source_lang=payload.get('source_lang', ''),
        target_lang=payload.get('target_lang', ''),
        granularity=payload.get('granularity', ''),
    )


def _pair_to_dict(pair: AlignedPair) -> dict:
    return {
        'source': [_segment_to_dict(segment) for segment in pair.source],
        'target': [_segment_to_dict(segment) for segment in pair.target],
        'score': pair.score,
    }


def _pair_from_dict(payload: dict) -> AlignedPair:
    return AlignedPair(
        source=[_segment_from_dict(item) for item in payload.get('source', [])],
        target=[_segment_from_dict(item) for item in payload.get('target', [])],
        score=float(payload.get('score', 0.0)),
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
        spans=[_span_from_dict(item) for item in payload.get('spans', [])],
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
