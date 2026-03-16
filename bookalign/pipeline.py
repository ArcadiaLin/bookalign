"""Pipeline helpers for extraction, alignment, and EPUB building."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ebooklib import epub

from bookalign.align.aligner import align_segments
from bookalign.align.base import BaseAligner
from bookalign.align.bertalign_adapter import BertalignAdapter
from bookalign.epub.builder import build_bilingual_epub
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


def align_extracted_chapters(
    source_chapters: list[ExtractedChapter],
    target_chapters: list[ExtractedChapter],
    *,
    source_lang: str,
    target_lang: str,
    aligner: BaseAligner | None = None,
) -> AlignmentResult:
    """Align extracted chapters in spine order."""

    engine = aligner or BertalignAdapter(
        src_lang=source_lang,
        tgt_lang=target_lang,
    )

    pairs = []
    for source_chapter, target_chapter in zip(source_chapters, target_chapters):
        chapter_result = align_segments(
            source_chapter.segments,
            target_chapter.segments,
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
        aligner=aligner,
    )


def run_bilingual_epub_pipeline(
    *,
    source_epub_path: str | Path,
    target_epub_path: str | Path,
    output_path: str | Path,
    source_lang: str = 'zh',
    target_lang: str = 'ja',
    aligner: BaseAligner | None = None,
) -> AlignmentResult:
    """Run the end-to-end pipeline and write a bilingual EPUB."""

    source_book = read_epub(source_epub_path)
    target_book = read_epub(target_epub_path)

    alignment = align_books(
        source_book,
        target_book,
        source_lang=source_lang,
        target_lang=target_lang,
        aligner=aligner,
    )
    build_bilingual_epub(
        alignment=alignment,
        source_book=source_book,
        target_book=target_book,
        output_path=Path(output_path),
    )
    return alignment
