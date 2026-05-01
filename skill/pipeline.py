"""Extraction and chapter-matching helpers for skill-style workflows."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ebooklib import epub

from epub.extractor import extract_segments
from epub.reader import get_spine_documents
from epub.sentence_splitter import SentenceSplitter
from models.types import Segment


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
_CHAPTER_HEADING_RE = re.compile(
    r'^(?:'
    r'(?:chapter|book|part)\s+[0-9ivxlcdm]+'
    r'|第\s*[一二三四五六七八九十百千〇零两兩0-9]+\s*[章节回部篇卷]'
    r')$',
    re.IGNORECASE,
)
_HEADING_PUNCT_RE = re.compile(r'[。．！？!?…]|\.{3,}')
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
    chapter_match_mode: str = 'raw',
) -> list[ChapterMatch]:
    """Match chapter sequences while allowing front/back matter skips."""

    if chapter_match_mode != 'raw':
        raise ValueError(
            "Unsupported chapter_match_mode: "
            f"{chapter_match_mode}; only 'raw' is supported"
        )

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
                )
                if skip_source < scores[i + 1][j]:
                    scores[i + 1][j] = skip_source
                    back[i + 1][j] = ('skip_source', i, j)

            if j < tgt_len:
                skip_target = current + _chapter_skip_penalty(
                    target_chapters[j],
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
                    ),
                )
            )

        i = prev_i
        j = prev_j

    matches.reverse()
    return matches


def _chapter_pair_score(
    source_chapter: ExtractedChapter,
    target_chapter: ExtractedChapter,
    *,
    src_idx: int,
    tgt_idx: int,
    src_total: int,
    tgt_total: int,
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
) -> float:
    src_count = max(source_chapter.sentence_count, 1)
    tgt_count = max(target_chapter.sentence_count, 1)
    count_cost = abs(math.log((src_count + 5) / (tgt_count + 5)))

    src_marker = _chapter_marker(source_chapter)
    tgt_marker = _chapter_marker(target_chapter)
    marker_cost = 0.0
    if src_marker is not None and tgt_marker is not None:
        marker_cost += -0.25 if src_marker == tgt_marker else 0.75

    position_cost = abs((src_idx + 1) / src_total - (tgt_idx + 1) / tgt_total) * 0.75
    return max(0.0, count_cost + marker_cost + position_cost)


def _chapter_skip_penalty(
    chapter: ExtractedChapter,
) -> float:
    count = chapter.sentence_count
    return 0.75 + min(count, 120) / 60.0


def _is_structured_paratext(
    chapter: ExtractedChapter,
    *,
    chapter_idx: int,
    structural_paratext_indexes: set[int],
) -> bool:
    return chapter_idx in structural_paratext_indexes


def _chapter_label(chapter: ExtractedChapter) -> str:
    title = (getattr(chapter.doc, 'title', '') or '').strip()
    if title:
        return title
    if hasattr(chapter.doc, 'get_name'):
        return chapter.doc.get_name()
    return ''


def _structural_paratext_indexes(chapters: list[ExtractedChapter]) -> set[int]:
    return set()


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
