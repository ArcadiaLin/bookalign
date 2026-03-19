"""Pipeline helpers for extraction, alignment, and EPUB building."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re

from ebooklib import epub

from bookalign.alignment_json import load_alignment_result, save_alignment_result
from bookalign.align.aligner import align_segments
from bookalign.align.base import BaseAligner
from bookalign.align.bertalign_adapter import BertalignAdapter
from bookalign.epub.builder import (
    build_bilingual_epub,
    build_bilingual_epub_on_source_layout,
)
from bookalign.epub.extractor import extract_segments
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.models.types import AlignmentResult, Segment


@dataclass
class ExtractedChapter:
    """Sentence-level extracted chapter content."""

    spine_idx: int
    doc: epub.EpubHtml
    segments: list[Segment]
    alignment_segments: list[Segment]
    retained_segments: list[Segment]

    @property
    def sentence_count(self) -> int:
        return len(self.alignment_segments)


@dataclass
class ChapterMatch:
    """A matched source/target chapter pair used for sentence alignment."""

    source_chapter: ExtractedChapter
    target_chapter: ExtractedChapter
    score: float


_PARATEXT_TITLE_RE = re.compile(
    r'(?:'
    r'cover|title|toc|contents|copyright|license|colophon|preface|foreword|'
    r'acknowledg|appendix|index|about|notes?|postscript|afterword|section0+|'
    r'封面|版权|版權|目录|目次|书籍信息|書籍情報|说明|說明|前言|后记|後記|译后记|譯後記|'
    r'附录|附錄|附记|附記|注\s*解|註\s*解|解説|解說|年\s*谱|年\s*譜|'
    r'参考文献|參考文獻|人と文学|について|表紙|奥付|あとがき'
    r')',
    re.IGNORECASE,
)
_CHAPTER_MARKER_RE = re.compile(r'第?\s*([0-9]+|[一二三四五六七八九十百千〇零两兩]+)\s*[章节回部篇卷]?')
_CJK_NUMERALS = {
    '零': 0,
    '〇': 0,
    '一': 1,
    '二': 2,
    '两': 2,
    '兩': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
}
_CJK_UNITS = {
    '十': 10,
    '百': 100,
    '千': 1000,
}


def extract_sentence_chapters(
    book: epub.EpubBook,
    *,
    language: str,
    extract_mode: str = 'filtered_preserve',
) -> list[ExtractedChapter]:
    """Extract sentence segments from each readable spine document."""

    splitter = SentenceSplitter(language=language)
    chapters: list[ExtractedChapter] = []
    for spine_idx, doc in get_spine_documents(book):
        segments = extract_segments(
            book,
            doc,
            chapter_idx=spine_idx,
            splitter=splitter,
            extract_mode=extract_mode,
        )
        if segments:
            alignment_segments = [segment for segment in segments if segment.alignment_role == 'align']
            retained_segments = [segment for segment in segments if segment.alignment_role != 'align']
            chapters.append(
                ExtractedChapter(
                    spine_idx=spine_idx,
                    doc=doc,
                    segments=segments,
                    alignment_segments=alignment_segments,
                    retained_segments=retained_segments,
                )
            )
    return chapters


def match_extracted_chapters(
    source_chapters: list[ExtractedChapter],
    target_chapters: list[ExtractedChapter],
    *,
    chapter_match_mode: str = 'structured',
) -> list[ChapterMatch]:
    """Match chapter sequences while allowing front/back matter skips."""

    if chapter_match_mode not in {'structured', 'raw'}:
        raise ValueError(f'Unsupported chapter_match_mode: {chapter_match_mode}')

    src_len = len(source_chapters)
    tgt_len = len(target_chapters)
    scores = [[math.inf] * (tgt_len + 1) for _ in range(src_len + 1)]
    back: list[list[tuple[str, int, int] | None]] = [
        [None] * (tgt_len + 1) for _ in range(src_len + 1)
    ]
    scores[0][0] = 0.0

    for i in range(src_len + 1):
        for j in range(tgt_len + 1):
            current = scores[i][j]
            if math.isinf(current):
                continue

            if i < src_len:
                skip_source = current + _chapter_skip_penalty(
                    source_chapters[i],
                    chapter_match_mode=chapter_match_mode,
                )
                if skip_source < scores[i + 1][j]:
                    scores[i + 1][j] = skip_source
                    back[i + 1][j] = ('skip_source', i, j)

            if j < tgt_len:
                skip_target = current + _chapter_skip_penalty(
                    target_chapters[j],
                    chapter_match_mode=chapter_match_mode,
                )
                if skip_target < scores[i][j + 1]:
                    scores[i][j + 1] = skip_target
                    back[i][j + 1] = ('skip_target', i, j)

            if i < src_len and j < tgt_len:
                pair_cost = current + _chapter_pair_cost(
                    source_chapters[i],
                    target_chapters[j],
                    src_idx=i,
                    tgt_idx=j,
                    src_total=src_len,
                    tgt_total=tgt_len,
                    chapter_match_mode=chapter_match_mode,
                )
                if pair_cost < scores[i + 1][j + 1]:
                    scores[i + 1][j + 1] = pair_cost
                    back[i + 1][j + 1] = ('match', i, j)

    matches: list[ChapterMatch] = []
    i = src_len
    j = tgt_len
    while i > 0 or j > 0:
        move = back[i][j]
        if move is None:
            break

        op, prev_i, prev_j = move
        if op == 'match':
            source_chapter = source_chapters[prev_i]
            target_chapter = target_chapters[prev_j]
            matches.append(
                ChapterMatch(
                    source_chapter=source_chapter,
                    target_chapter=target_chapter,
                    score=_chapter_pair_score(
                        source_chapter,
                        target_chapter,
                        src_idx=prev_i,
                        tgt_idx=prev_j,
                        src_total=src_len,
                        tgt_total=tgt_len,
                        chapter_match_mode=chapter_match_mode,
                    ),
                )
            )

        i = prev_i
        j = prev_j

    matches.reverse()
    substantive = [
        match
        for match in matches
        if _should_keep_chapter_match(
            match.source_chapter,
            match.target_chapter,
            chapter_match_mode=chapter_match_mode,
        )
    ]
    return substantive or matches


def _chapter_pair_score(
    source_chapter: ExtractedChapter,
    target_chapter: ExtractedChapter,
    *,
    src_idx: int,
    tgt_idx: int,
    src_total: int,
    tgt_total: int,
    chapter_match_mode: str,
) -> float:
    return max(
        0.0,
        3.0
        - _chapter_pair_cost(
            source_chapter,
            target_chapter,
            src_idx=src_idx,
            tgt_idx=tgt_idx,
            src_total=src_total,
            tgt_total=tgt_total,
            chapter_match_mode=chapter_match_mode,
        ),
    )


def _chapter_pair_cost(
    source_chapter: ExtractedChapter,
    target_chapter: ExtractedChapter,
    *,
    src_idx: int,
    tgt_idx: int,
    src_total: int,
    tgt_total: int,
    chapter_match_mode: str,
) -> float:
    src_count = max(source_chapter.sentence_count, 1)
    tgt_count = max(target_chapter.sentence_count, 1)
    count_cost = abs(math.log((src_count + 5) / (tgt_count + 5)))

    paratext_cost = 0.0
    if chapter_match_mode == 'structured':
        src_paratext = _looks_like_paratext(source_chapter)
        tgt_paratext = _looks_like_paratext(target_chapter)
        if src_paratext != tgt_paratext:
            paratext_cost += 1.2
        elif src_paratext and tgt_paratext:
            paratext_cost += 0.4

    src_marker = _chapter_marker(source_chapter)
    tgt_marker = _chapter_marker(target_chapter)
    marker_cost = 0.0
    if src_marker is not None and tgt_marker is not None:
        marker_cost += -0.8 if src_marker == tgt_marker else 2.0
    elif src_marker is not None or tgt_marker is not None:
        marker_cost += 0.35

    position_cost = abs((src_idx + 1) / src_total - (tgt_idx + 1) / tgt_total) * 0.75
    return max(0.0, count_cost + paratext_cost + marker_cost + position_cost)


def _chapter_skip_penalty(
    chapter: ExtractedChapter,
    *,
    chapter_match_mode: str,
) -> float:
    count = chapter.sentence_count
    if count >= 120:
        base = 4.0
    elif count >= 40:
        base = 2.5
    elif count >= 12:
        base = 1.2
    else:
        base = 0.4
    if chapter_match_mode == 'structured' and _looks_like_paratext(chapter):
        return base * 0.25
    return base


def _should_keep_chapter_match(
    source_chapter: ExtractedChapter,
    target_chapter: ExtractedChapter,
    *,
    chapter_match_mode: str,
) -> bool:
    if chapter_match_mode != 'structured':
        return True
    if source_chapter.sentence_count >= 20 or target_chapter.sentence_count >= 20:
        return True
    return not (_looks_like_paratext(source_chapter) or _looks_like_paratext(target_chapter))


def _looks_like_paratext(chapter: ExtractedChapter) -> bool:
    label = _chapter_label(chapter).casefold()
    if _PARATEXT_TITLE_RE.search(label):
        return True
    preview_segments = chapter.alignment_segments or chapter.segments
    preview = ' '.join(segment.text for segment in preview_segments[:3]).casefold()
    if _PARATEXT_TITLE_RE.search(preview):
        return True
    return False


def _chapter_marker(chapter: ExtractedChapter) -> int | None:
    title = (getattr(chapter.doc, 'title', '') or '').strip()
    if not title:
        return None
    match = _CHAPTER_MARKER_RE.search(title)
    if not match:
        return None
    token = match.group(1)
    if token.isdigit():
        return int(token)
    return _parse_cjk_numeral(token)


def _chapter_label(chapter: ExtractedChapter) -> str:
    title = (getattr(chapter.doc, 'title', '') or '').strip()
    if title:
        return title
    if hasattr(chapter.doc, 'get_name'):
        return chapter.doc.get_name()
    return ''


def _parse_cjk_numeral(token: str) -> int | None:
    if not token:
        return None
    if all(char in _CJK_NUMERALS for char in token):
        value = 0
        for char in token:
            value = value * 10 + _CJK_NUMERALS[char]
        return value

    total = 0
    current = 0
    for char in token:
        if char in _CJK_NUMERALS:
            current = _CJK_NUMERALS[char]
            continue
        unit = _CJK_UNITS.get(char)
        if unit is None:
            return None
        total += (current or 1) * unit
        current = 0
    return total + current


def align_extracted_chapters(
    source_chapters: list[ExtractedChapter],
    target_chapters: list[ExtractedChapter],
    *,
    source_lang: str,
    target_lang: str,
    chapter_match_mode: str = 'structured',
    aligner: BaseAligner | None = None,
    enable_local_realign: bool = False,
) -> AlignmentResult:
    """Align extracted chapters in spine order."""

    engine = aligner or BertalignAdapter(
        src_lang=source_lang,
        tgt_lang=target_lang,
    )

    pairs = []
    chapter_matches = match_extracted_chapters(
        source_chapters,
        target_chapters,
        chapter_match_mode=chapter_match_mode,
    )
    for chapter_match in chapter_matches:
        chapter_result = align_segments(
            chapter_match.source_chapter.alignment_segments,
            chapter_match.target_chapter.alignment_segments,
            source_lang=source_lang,
            target_lang=target_lang,
            granularity='sentence',
            aligner=engine,
        )
        if enable_local_realign:
            chapter_result = _realign_suspect_windows(
                chapter_result,
                src_segments=chapter_match.source_chapter.alignment_segments,
                tgt_segments=chapter_match.target_chapter.alignment_segments,
                source_lang=source_lang,
                target_lang=target_lang,
                aligner=engine,
            )
        pairs.extend(chapter_result.pairs)

    return AlignmentResult(
        pairs=pairs,
        source_lang=source_lang,
        target_lang=target_lang,
        granularity='sentence',
        retained_source_segments=[
            segment
            for chapter in source_chapters
            for segment in chapter.retained_segments
        ],
        retained_target_segments=[
            segment
            for chapter in target_chapters
            for segment in chapter.retained_segments
        ],
    )


def _realign_suspect_windows(
    alignment: AlignmentResult,
    *,
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    source_lang: str,
    target_lang: str,
    aligner: BaseAligner,
) -> AlignmentResult:
    if len(alignment.pairs) < 6:
        return alignment

    src_lookup = {id(segment): idx for idx, segment in enumerate(src_segments)}
    tgt_lookup = {id(segment): idx for idx, segment in enumerate(tgt_segments)}
    local_aligner = _build_local_realign_aligner(
        aligner,
        source_lang=source_lang,
        target_lang=target_lang,
    )
    pairs = list(alignment.pairs)
    for _ in range(4):
        pair_ranges = _merge_pair_ranges(_detect_suspect_pair_ranges(pairs))
        if not pair_ranges:
            break
        suspect_start, suspect_end = pair_ranges[0]
        segment_window = _expand_pair_range_to_segment_window(
            pairs,
            suspect_start=suspect_start,
            suspect_end=suspect_end,
            src_lookup=src_lookup,
            tgt_lookup=tgt_lookup,
            src_total=len(src_segments),
            tgt_total=len(tgt_segments),
        )
        if segment_window is None:
            continue
        src_start, src_end, tgt_start, tgt_end = segment_window
        replace_start, replace_end = _pair_index_span_for_segment_window(
            pairs,
            src_lookup=src_lookup,
            tgt_lookup=tgt_lookup,
            src_start=src_start,
            src_end=src_end,
            tgt_start=tgt_start,
            tgt_end=tgt_end,
        )
        if replace_start is None or replace_end is None:
            continue

        original_window = pairs[replace_start : replace_end + 1]
        candidate = align_segments(
            src_segments[src_start : src_end + 1],
            tgt_segments[tgt_start : tgt_end + 1],
            source_lang=source_lang,
            target_lang=target_lang,
            granularity='sentence',
            aligner=local_aligner,
        ).pairs
        if not candidate:
            continue
        if not _should_accept_realign_candidate(original_window, candidate):
            break
        pairs[replace_start : replace_end + 1] = candidate
        pairs = _rerun_suffix_after_window(
            pairs,
            replace_end=replace_end,
            src_segments=src_segments,
            tgt_segments=tgt_segments,
            src_lookup=src_lookup,
            tgt_lookup=tgt_lookup,
            source_lang=source_lang,
            target_lang=target_lang,
            aligner=aligner,
        )

    return AlignmentResult(
        pairs=pairs,
        source_lang=alignment.source_lang,
        target_lang=alignment.target_lang,
        granularity=alignment.granularity,
        extract_mode=alignment.extract_mode,
        retained_source_segments=alignment.retained_source_segments,
        retained_target_segments=alignment.retained_target_segments,
    )


def _build_local_realign_aligner(
    aligner: BaseAligner,
    *,
    source_lang: str,
    target_lang: str,
) -> BaseAligner:
    if isinstance(aligner, BertalignAdapter):
        return BertalignAdapter(
            model_name=aligner.model_name,
            max_align=min(2, aligner.max_align),
            top_k=min(2, aligner.top_k),
            win=max(2, min(aligner.win, 3)),
            skip=min(aligner.skip, -0.8),
            margin=aligner.margin,
            len_penalty=aligner.len_penalty,
            src_lang=source_lang,
            tgt_lang=target_lang,
            default_score=aligner.default_score,
        )
    return aligner


def _rerun_suffix_after_window(
    pairs: list,
    *,
    replace_end: int,
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    src_lookup: dict[int, int],
    tgt_lookup: dict[int, int],
    source_lang: str,
    target_lang: str,
    aligner: BaseAligner,
) -> list:
    consumed_src = [
        src_lookup[id(segment)]
        for pair in pairs[: replace_end + 1]
        for segment in pair.source
        if id(segment) in src_lookup
    ]
    consumed_tgt = [
        tgt_lookup[id(segment)]
        for pair in pairs[: replace_end + 1]
        for segment in pair.target
        if id(segment) in tgt_lookup
    ]
    if not consumed_src or not consumed_tgt:
        return pairs

    next_src = max(consumed_src) + 1
    next_tgt = max(consumed_tgt) + 1
    if next_src >= len(src_segments) or next_tgt >= len(tgt_segments):
        return pairs

    original_suffix = pairs[replace_end + 1 :]
    candidate_suffix = align_segments(
        src_segments[next_src:],
        tgt_segments[next_tgt:],
        source_lang=source_lang,
        target_lang=target_lang,
        granularity='sentence',
        aligner=aligner,
    ).pairs
    if not candidate_suffix:
        return pairs
    if original_suffix:
        original_prefix = original_suffix[:12]
        candidate_prefix = candidate_suffix[:12]
        if candidate_prefix and not _should_accept_realign_candidate(original_prefix, candidate_prefix):
            return pairs
    if original_suffix and not _should_accept_realign_candidate(original_suffix, candidate_suffix):
        return pairs
    return [*pairs[: replace_end + 1], *candidate_suffix]


def _detect_suspect_pair_ranges(pairs: list) -> list[tuple[int, int]]:
    total = len(pairs)
    if total < 6:
        return []

    window_size = min(8, max(6, total))
    lookback_size = min(6, max(3, total // 8))
    boundary = 60 if total > 160 else max(0, total // 8)
    flagged: list[tuple[int, int]] = []

    for start in range(0, total - window_size + 1):
        end = start + window_size - 1
        if boundary and (end < boundary or start >= total - boundary):
            continue
        window = pairs[start : end + 1]
        lookback_start = max(0, start - lookback_size)
        lookback = pairs[lookback_start:start]
        if lookback and _one_to_one_ratio(lookback) < 0.6:
            continue
        big = sum(1 for pair in window if _is_big_bead(pair))
        skip = sum(1 for pair in window if _is_skip_pair(pair))
        extreme = sum(1 for pair in window if _has_extreme_length_ratio(pair))
        if (
            (big >= 3 and skip >= 1)
            or big >= 4
            or ((big + skip) >= 3 and extreme >= 2)
        ):
            flagged.append((start, end))
    return flagged


def _merge_pair_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append((start, end))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def _expand_pair_range_to_segment_window(
    pairs: list,
    *,
    suspect_start: int,
    suspect_end: int,
    src_lookup: dict[int, int],
    tgt_lookup: dict[int, int],
    src_total: int,
    tgt_total: int,
) -> tuple[int, int, int, int] | None:
    src_indices = [
        src_lookup[id(segment)]
        for pair in pairs[suspect_start : suspect_end + 1]
        for segment in pair.source
        if id(segment) in src_lookup
    ]
    tgt_indices = [
        tgt_lookup[id(segment)]
        for pair in pairs[suspect_start : suspect_end + 1]
        for segment in pair.target
        if id(segment) in tgt_lookup
    ]
    if not src_indices or not tgt_indices:
        return None
    context = 10
    return (
        max(0, min(src_indices) - context),
        min(src_total - 1, max(src_indices) + context),
        max(0, min(tgt_indices) - context),
        min(tgt_total - 1, max(tgt_indices) + context),
    )


def _pair_index_span_for_segment_window(
    pairs: list,
    *,
    src_lookup: dict[int, int],
    tgt_lookup: dict[int, int],
    src_start: int,
    src_end: int,
    tgt_start: int,
    tgt_end: int,
) -> tuple[int | None, int | None]:
    matching_indices = [
        idx
        for idx, pair in enumerate(pairs)
        if _pair_overlaps_segment_window(
            pair,
            src_lookup=src_lookup,
            tgt_lookup=tgt_lookup,
            src_start=src_start,
            src_end=src_end,
            tgt_start=tgt_start,
            tgt_end=tgt_end,
        )
    ]
    if not matching_indices:
        return None, None
    return matching_indices[0], matching_indices[-1]


def _pair_overlaps_segment_window(
    pair,
    *,
    src_lookup: dict[int, int],
    tgt_lookup: dict[int, int],
    src_start: int,
    src_end: int,
    tgt_start: int,
    tgt_end: int,
) -> bool:
    for segment in pair.source:
        idx = src_lookup.get(id(segment))
        if idx is not None and src_start <= idx <= src_end:
            return True
    for segment in pair.target:
        idx = tgt_lookup.get(id(segment))
        if idx is not None and tgt_start <= idx <= tgt_end:
            return True
    return False


def _should_accept_realign_candidate(original_pairs: list, candidate_pairs: list) -> bool:
    original = _window_metrics(original_pairs)
    candidate = _window_metrics(candidate_pairs)
    if candidate['score'] <= original['score']:
        return False
    if candidate['skip'] > original['skip']:
        return False
    if candidate['big'] > original['big']:
        return False
    return candidate['one_to_one'] >= original['one_to_one']


def _window_metrics(pairs: list) -> dict[str, float]:
    one_to_one = sum(1 for pair in pairs if len(pair.source) == 1 and len(pair.target) == 1)
    skip = sum(1 for pair in pairs if _is_skip_pair(pair))
    big = sum(1 for pair in pairs if _is_big_bead(pair))
    extreme = sum(1 for pair in pairs if _has_extreme_length_ratio(pair))
    score = one_to_one * 3.0 - skip * 2.5 - big * 2.0 - extreme * 1.0
    return {
        'one_to_one': one_to_one,
        'skip': skip,
        'big': big,
        'extreme': extreme,
        'score': score,
    }


def _one_to_one_ratio(pairs: list) -> float:
    if not pairs:
        return 0.0
    one_to_one = sum(1 for pair in pairs if len(pair.source) == 1 and len(pair.target) == 1)
    return one_to_one / len(pairs)


def _is_skip_pair(pair) -> bool:
    return not pair.source or not pair.target


def _is_big_bead(pair) -> bool:
    src_count = len(pair.source)
    tgt_count = len(pair.target)
    if src_count == 0 or tgt_count == 0:
        return False
    if (src_count, tgt_count) in {(1, 1), (1, 2), (2, 1), (2, 2)}:
        return False
    return src_count >= 3 or tgt_count >= 3


def _has_extreme_length_ratio(pair) -> bool:
    if not pair.source or not pair.target:
        return False
    src_len = max(1, sum(len(segment.text.strip()) for segment in pair.source))
    tgt_len = max(1, sum(len(segment.text.strip()) for segment in pair.target))
    ratio = max(src_len / tgt_len, tgt_len / src_len)
    return ratio >= 3.5


def align_books(
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    *,
    source_lang: str,
    target_lang: str,
    chapter_match_mode: str | None = None,
    extract_mode: str = 'filtered_preserve',
    aligner: BaseAligner | None = None,
    enable_local_realign: bool = False,
) -> AlignmentResult:
    """Extract and align two books chapter by chapter."""

    resolved_match_mode = _resolve_chapter_match_mode(chapter_match_mode, extract_mode=extract_mode)
    source_chapters = extract_sentence_chapters(source_book, language=source_lang, extract_mode=extract_mode)
    target_chapters = extract_sentence_chapters(target_book, language=target_lang, extract_mode=extract_mode)
    source_alignment_chapters = [chapter for chapter in source_chapters if chapter.alignment_segments]
    target_alignment_chapters = [chapter for chapter in target_chapters if chapter.alignment_segments]
    result = align_extracted_chapters(
        source_alignment_chapters,
        target_alignment_chapters,
        source_lang=source_lang,
        target_lang=target_lang,
        chapter_match_mode=resolved_match_mode,
        aligner=aligner,
        enable_local_realign=enable_local_realign,
    )
    result.extract_mode = extract_mode
    result.retained_source_segments = [
        segment
        for chapter in source_chapters
        for segment in chapter.retained_segments
    ]
    result.retained_target_segments = [
        segment
        for chapter in target_chapters
        for segment in chapter.retained_segments
    ]
    return result


def _resolve_chapter_match_mode(chapter_match_mode: str | None, *, extract_mode: str) -> str:
    if extract_mode != 'filtered_preserve':
        raise ValueError(f'Unsupported extract_mode: {extract_mode}')
    if chapter_match_mode is not None:
        return chapter_match_mode
    return 'structured'


def run_bilingual_epub_pipeline(
    *,
    source_epub_path: str | Path,
    target_epub_path: str | Path,
    output_path: str | Path,
    source_lang: str = 'ja',
    target_lang: str = 'zh',
    builder_mode: str = 'simple',
    chapter_match_mode: str | None = None,
    extract_mode: str = 'filtered_preserve',
    alignment_json_input_path: str | Path | None = None,
    alignment_json_output_path: str | Path | None = None,
    writeback_mode: str = 'paragraph',
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    aligner: BaseAligner | None = None,
    enable_local_realign: bool = False,
) -> AlignmentResult:
    """Run the end-to-end pipeline and write a bilingual EPUB."""

    if layout_direction not in {'horizontal', 'source'}:
        raise ValueError(f'Unsupported layout_direction: {layout_direction}')
    if writeback_mode not in {'paragraph', 'inline'}:
        raise ValueError(f'Unsupported writeback_mode: {writeback_mode}')

    source_book = read_epub(source_epub_path)
    target_book = read_epub(target_epub_path)

    if alignment_json_input_path is not None:
        alignment = load_alignment_result(alignment_json_input_path)
    else:
        alignment = align_books(
            source_book,
            target_book,
            source_lang=source_lang,
            target_lang=target_lang,
            chapter_match_mode=chapter_match_mode,
            extract_mode=extract_mode,
            aligner=aligner,
            enable_local_realign=enable_local_realign,
        )
        if alignment_json_output_path is not None:
            save_alignment_result(alignment, alignment_json_output_path)

    build_bilingual_epub_from_alignment(
        alignment=alignment,
        source_book=source_book,
        target_book=target_book,
        output_path=output_path,
        builder_mode=builder_mode,
        writeback_mode=writeback_mode,
        layout_direction=layout_direction,
        emit_translation_metadata=emit_translation_metadata,
        normalize_vertical_punctuation=normalize_vertical_punctuation,
        extract_mode=extract_mode,
    )
    return alignment


def build_bilingual_epub_from_alignment(
    *,
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: str | Path,
    builder_mode: str = 'simple',
    writeback_mode: str = 'paragraph',
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    extract_mode: str = 'filtered_preserve',
) -> None:
    if builder_mode == 'simple':
        build_bilingual_epub(
            alignment=alignment,
            source_book=source_book,
            target_book=target_book,
            output_path=Path(output_path),
        )
        return
    if builder_mode == 'source_layout':
        build_bilingual_epub_on_source_layout(
            alignment=alignment,
            source_book=source_book,
            target_book=target_book,
            output_path=Path(output_path),
            writeback_mode=writeback_mode,
            layout_direction=layout_direction,
            emit_translation_metadata=emit_translation_metadata,
            normalize_vertical_punctuation=normalize_vertical_punctuation,
            extract_mode=extract_mode,
        )
        return
    raise ValueError(f'Unsupported builder_mode: {builder_mode}')


def build_bilingual_epub_from_alignment_json(
    *,
    source_epub_path: str | Path,
    target_epub_path: str | Path,
    alignment_json_path: str | Path,
    output_path: str | Path,
    builder_mode: str = 'simple',
    writeback_mode: str = 'paragraph',
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    extract_mode: str = 'filtered_preserve',
) -> AlignmentResult:
    source_book = read_epub(source_epub_path)
    target_book = read_epub(target_epub_path)
    alignment = load_alignment_result(alignment_json_path)
    build_bilingual_epub_from_alignment(
        alignment=alignment,
        source_book=source_book,
        target_book=target_book,
        output_path=output_path,
        builder_mode=builder_mode,
        writeback_mode=writeback_mode,
        layout_direction=layout_direction,
        emit_translation_metadata=emit_translation_metadata,
        normalize_vertical_punctuation=normalize_vertical_punctuation,
        extract_mode=extract_mode,
    )
    return alignment
