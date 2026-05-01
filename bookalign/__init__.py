"""BookAlign public package API."""

from bookalign.api import (
    extract_book,
    get_chapter_count,
    get_chapter_records,
    list_chapters,
    load_epub,
    load_extraction_json,
    save_extraction_json,
)
from bookalign.models.types import (
    AlignmentResult,
    AlignedPair,
    BookExtraction,
    ChapterInfo,
    Segment,
    SegmentRecord,
)

__all__ = [
    'AlignedPair',
    'AlignmentResult',
    'BookExtraction',
    'ChapterInfo',
    'Segment',
    'SegmentRecord',
    'extract_book',
    'get_chapter_count',
    'get_chapter_records',
    'list_chapters',
    'load_epub',
    'load_extraction_json',
    'save_extraction_json',
]
