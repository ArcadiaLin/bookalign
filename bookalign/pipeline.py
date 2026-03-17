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

    @property
    def sentence_count(self) -> int:
        return len(self.segments)


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
        )
        if segments:
            chapters.append(
                ExtractedChapter(
                    spine_idx=spine_idx,
                    doc=doc,
                    segments=segments,
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
    preview = ' '.join(segment.text for segment in chapter.segments[:3]).casefold()
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
            chapter_match.source_chapter.segments,
            chapter_match.target_chapter.segments,
            source_lang=source_lang,
            target_lang=target_lang,
            granularity='sentence',
            aligner=engine,
        )
        pairs.extend(chapter_result.pairs)

    return AlignmentResult(
        pairs=pairs,
        source_lang=source_lang,
        target_lang=target_lang,
        granularity='sentence',
    )


def align_books(
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    *,
    source_lang: str,
    target_lang: str,
    chapter_match_mode: str = 'structured',
    aligner: BaseAligner | None = None,
) -> AlignmentResult:
    """Extract and align two books chapter by chapter."""

    source_chapters = extract_sentence_chapters(source_book, language=source_lang)
    target_chapters = extract_sentence_chapters(target_book, language=target_lang)
    return align_extracted_chapters(
        source_chapters,
        target_chapters,
        source_lang=source_lang,
        target_lang=target_lang,
        chapter_match_mode=chapter_match_mode,
        aligner=aligner,
    )


def run_bilingual_epub_pipeline(
    *,
    source_epub_path: str | Path,
    target_epub_path: str | Path,
    output_path: str | Path,
    source_lang: str = 'ja',
    target_lang: str = 'zh',
    builder_mode: str = 'simple',
    chapter_match_mode: str = 'structured',
    alignment_json_input_path: str | Path | None = None,
    alignment_json_output_path: str | Path | None = None,
    writeback_mode: str = 'paragraph',
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    aligner: BaseAligner | None = None,
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
            aligner=aligner,
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
    )
    return alignment
