"""High-level engineering APIs for EPUB extraction."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from ebooklib import epub

from epub.extractor import extract_segments
from epub.reader import get_spine_documents, read_epub
from extraction_json import load_extraction_result, save_extraction_result
from models.types import BookExtraction, ChapterInfo, SegmentRecord
from pipeline import (
    _chapter_label,
    _is_structured_paratext,
    _structural_paratext_indexes,
    extract_sentence_chapters,
)

_NON_WORD_RE = re.compile(r'[^\w]+', re.UNICODE)


def load_epub(path: str | Path) -> epub.EpubBook:
    """Read an EPUB and return the parsed book object."""

    return read_epub(path)


def extract_book(
    source: str | Path | epub.EpubBook,
    *,
    language: str,
    granularity: str = 'sentence',
    extract_mode: str = 'filtered_preserve',
) -> BookExtraction:
    """Extract one EPUB into chapter metadata plus sentence and paragraph records."""

    if granularity not in {'sentence', 'paragraph'}:
        raise ValueError(f'Unsupported granularity: {granularity}')

    source_path = ''
    if isinstance(source, (str, Path)):
        source_path = str(Path(source))
        book = load_epub(source)
    else:
        book = source

    sentence_chapters = extract_sentence_chapters(book, language=language, extract_mode=extract_mode)
    paragraph_records = _extract_paragraph_records(book, extract_mode=extract_mode)
    chapter_infos = _build_chapter_infos(sentence_chapters, paragraph_records)
    chapter_map = {chapter.chapter_idx: chapter for chapter in chapter_infos}
    sentence_records = _build_sentence_records(sentence_chapters, chapter_map)
    paragraph_records = _attach_paragraph_metadata(paragraph_records, chapter_map)

    return BookExtraction(
        language=language,
        extract_mode=extract_mode,
        default_granularity=granularity,
        chapters=chapter_infos,
        sentence_segments=sentence_records,
        paragraph_segments=paragraph_records,
        source_path=source_path,
    )


def save_extraction_json(extraction: BookExtraction, path: str | Path) -> Path:
    """Write single-book extraction JSON to disk."""

    return save_extraction_result(extraction, path)


def load_extraction_json(path: str | Path) -> BookExtraction:
    """Load single-book extraction JSON from disk."""

    return load_extraction_result(path)


def list_chapters(extraction: BookExtraction) -> list[ChapterInfo]:
    """Return inferred chapters in order."""

    return list(extraction.chapters)


def get_chapter_records(
    extraction: BookExtraction,
    chapter_ref: str | int,
    *,
    granularity: str | None = None,
    include_retained: bool = True,
    limit: int | None = None,
    offset: int = 0,
) -> list[SegmentRecord]:
    """Return ordered sentence or paragraph records for one chapter."""

    if offset < 0:
        raise ValueError('offset must be non-negative')
    if limit is not None and limit < 0:
        raise ValueError('limit must be non-negative')

    chapter = _resolve_chapter(extraction, chapter_ref)
    records = _records_for_granularity(extraction, granularity)
    items = [
        record
        for record in records
        if record.chapter_id == chapter.chapter_id
        and (include_retained or record.segment.alignment_role == 'align')
    ]
    items.sort(key=_segment_record_sort_key)
    if offset:
        items = items[offset:]
    if limit is not None:
        items = items[:limit]
    return items


def get_chapter_count(
    extraction: BookExtraction,
    chapter_ref: str | int,
    *,
    granularity: str | None = None,
    include_retained: bool = True,
) -> int:
    """Return record count for one chapter."""

    return len(
        get_chapter_records(
            extraction,
            chapter_ref,
            granularity=granularity,
            include_retained=include_retained,
        )
    )


def _extract_paragraph_records(
    book: epub.EpubBook,
    *,
    extract_mode: str,
) -> list[SegmentRecord]:
    records: list[SegmentRecord] = []
    for chapter_idx, doc in get_spine_documents(book):
        for segment in extract_segments(
            book,
            doc,
            chapter_idx=chapter_idx,
            splitter=None,
            extract_mode=extract_mode,
        ):
            records.append(
                SegmentRecord(
                    segment=segment,
                    chapter_id='',
                    chapter_title='',
                    granularity='paragraph',
                )
            )
    return records


def _build_chapter_infos(
    sentence_chapters,
    paragraph_records: list[SegmentRecord],
) -> list[ChapterInfo]:
    structural_paratext = _structural_paratext_indexes(sentence_chapters)
    paragraph_counts = Counter(record.segment.chapter_idx for record in paragraph_records)
    paragraph_alignment_counts = Counter(
        record.segment.chapter_idx
        for record in paragraph_records
        if record.segment.alignment_role == 'align'
    )
    chapter_ids = _generate_chapter_ids(sentence_chapters)

    chapters: list[ChapterInfo] = []
    for chapter_idx, sentence_chapter in enumerate(sentence_chapters):
        label = _chapter_label(sentence_chapter)
        chapter_id = chapter_ids[chapter_idx]
        chapters.append(
            ChapterInfo(
                chapter_id=chapter_id,
                chapter_idx=chapter_idx,
                spine_idx=sentence_chapter.spine_idx,
                title=(getattr(sentence_chapter.doc, 'title', '') or label).strip(),
                label=label,
                is_paratext=_is_structured_paratext(
                    sentence_chapter,
                    chapter_idx=chapter_idx,
                    structural_paratext_indexes=structural_paratext,
                ),
                sentence_count=len(sentence_chapter.segments),
                paragraph_count=paragraph_counts.get(sentence_chapter.spine_idx, 0),
                alignment_sentence_count=len(sentence_chapter.alignment_segments),
                alignment_paragraph_count=paragraph_alignment_counts.get(sentence_chapter.spine_idx, 0),
            )
        )
    return chapters


def _build_sentence_records(sentence_chapters, chapter_map: dict[int, ChapterInfo]) -> list[SegmentRecord]:
    records: list[SegmentRecord] = []
    for chapter_idx, chapter in enumerate(sentence_chapters):
        info = chapter_map[chapter_idx]
        for segment in chapter.segments:
            records.append(
                SegmentRecord(
                    segment=segment,
                    chapter_id=info.chapter_id,
                    chapter_title=info.title or info.label,
                    granularity='sentence',
                )
            )
    return records


def _attach_paragraph_metadata(
    paragraph_records: list[SegmentRecord],
    chapter_map: dict[int, ChapterInfo],
) -> list[SegmentRecord]:
    attached: list[SegmentRecord] = []
    for record in paragraph_records:
        chapter = chapter_map[_resolve_chapter_idx(chapter_map, record.segment.chapter_idx)]
        attached.append(
            SegmentRecord(
                segment=record.segment,
                chapter_id=chapter.chapter_id,
                chapter_title=chapter.title or chapter.label,
                granularity='paragraph',
            )
        )
    return attached


def _resolve_chapter(extraction: BookExtraction, chapter_ref: str | int) -> ChapterInfo:
    if isinstance(chapter_ref, str):
        for chapter in extraction.chapters:
            if chapter.chapter_id == chapter_ref:
                return chapter
        raise KeyError(f'Unknown chapter_id: {chapter_ref}')

    for chapter in extraction.chapters:
        if chapter.chapter_idx == chapter_ref:
            return chapter
    for chapter in extraction.chapters:
        if chapter.spine_idx == chapter_ref:
            return chapter
    raise KeyError(f'Unknown chapter reference: {chapter_ref}')


def _records_for_granularity(extraction: BookExtraction, granularity: str | None) -> list[SegmentRecord]:
    resolved = granularity or extraction.default_granularity
    if resolved == 'sentence':
        return extraction.sentence_segments
    if resolved == 'paragraph':
        return extraction.paragraph_segments
    raise ValueError(f'Unsupported granularity: {resolved}')


def _segment_record_sort_key(record: SegmentRecord) -> tuple[int, int, int]:
    return (
        record.segment.chapter_idx,
        record.segment.paragraph_idx,
        -1 if record.segment.sentence_idx is None else record.segment.sentence_idx,
    )


def _generate_chapter_ids(sentence_chapters) -> dict[int, str]:
    chapter_ids: dict[int, str] = {}
    seen: Counter[str] = Counter()
    for chapter_idx, chapter in enumerate(sentence_chapters):
        label = _chapter_label(chapter) or f'spine-{chapter.spine_idx:04d}'
        slug = _slugify_chapter_label(label) or f'spine-{chapter.spine_idx:04d}'
        seen[slug] += 1
        if seen[slug] > 1:
            slug = f'{slug}-{seen[slug]}'
        chapter_ids[chapter_idx] = slug
    return chapter_ids


def _slugify_chapter_label(label: str) -> str:
    normalized = _NON_WORD_RE.sub('-', label.strip().casefold()).strip('-')
    return normalized


def _resolve_chapter_idx(chapter_map: dict[int, ChapterInfo], chapter_idx: int) -> int:
    if chapter_idx in chapter_map:
        return chapter_idx
    for key, chapter in chapter_map.items():
        if chapter.spine_idx == chapter_idx:
            return key
    raise KeyError(f'Unknown chapter_idx/spine_idx: {chapter_idx}')


def list_book_chapters(extraction: BookExtraction, view: str = 'summary') -> dict:
    from service import list_book_chapters as _impl

    return _impl(extraction, view=view)


def get_chapter_preview(extraction: BookExtraction, chapter_id: str | int, max_chars: int = 300) -> dict:
    from service import get_chapter_preview as _impl

    return _impl(extraction, chapter_id, max_chars=max_chars)


def get_chapter_text(
    extraction: BookExtraction,
    chapter_id: str | int,
    granularity: str = 'paragraph',
    include_retained: bool = True,
    limit: int | None = None,
    offset: int = 0,
) -> dict:
    from service import get_chapter_text as _impl

    return _impl(
        extraction,
        chapter_id,
        granularity=granularity,
        include_retained=include_retained,
        limit=limit,
        offset=offset,
    )


def get_chapter_structure(extraction: BookExtraction, chapter_id: str | int) -> dict:
    from service import get_chapter_structure as _impl

    return _impl(extraction, chapter_id)


def search_book_text(extraction: BookExtraction, query: str, scope: str = 'all') -> dict:
    from service import search_book_text as _impl

    return _impl(extraction, query, scope=scope)


def list_extracted_chapters(extraction: BookExtraction) -> dict:
    from service import list_extracted_chapters as _impl

    return _impl(extraction)


def get_extracted_segments(
    extraction: BookExtraction,
    chapter_id: str | int,
    granularity: str = 'sentence',
    include_retained: bool = True,
) -> dict:
    from service import get_extracted_segments as _impl

    return _impl(
        extraction,
        chapter_id,
        granularity=granularity,
        include_retained=include_retained,
    )


def get_segment(extraction: BookExtraction, segment_id: str) -> dict:
    from service import get_segment as _impl

    return _impl(extraction, segment_id)


def resolve_cfi(extraction: BookExtraction, cfi: str) -> dict:
    from service import resolve_cfi as _impl

    return _impl(extraction, cfi)


def locate_text(extraction: BookExtraction, text_query: str, chapter_id: str | None = None) -> dict:
    from service import locate_text as _impl

    return _impl(extraction, text_query, chapter_id=chapter_id)


def get_segment_cfi(extraction: BookExtraction, segment_id: str) -> dict:
    from service import get_segment_cfi as _impl

    return _impl(extraction, segment_id)
