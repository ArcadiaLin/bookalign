from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("ebooklib")
pytest.importorskip("lxml")
pytest.importorskip("pysbd")

from ebooklib import epub

COPY_ROOT = Path(__file__).resolve().parents[1]
if str(COPY_ROOT) not in sys.path:
    sys.path.insert(0, str(COPY_ROOT))

import api  # noqa: E402
import service  # noqa: E402
from align.bertalign_adapter import BertalignAdapter  # noqa: E402


def _book(title: str, language: str, chapters: list[tuple[str, str]]) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language(language)

    docs = []
    for index, (chapter_title, body) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f"chapter{index}.xhtml",
            lang=language,
        )
        chapter.set_content(body)
        book.add_item(chapter)
        docs.append(chapter)

    book.spine = docs
    book.toc = tuple(docs)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    return book


def _write_book(book: epub.EpubBook, path: Path) -> Path:
    epub.write_epub(str(path), book)
    return path


class StubBertalignAdapter(BertalignAdapter):
    def __init__(self):
        pass

    def align(self, src_texts, tgt_texts):
        return [([index], [index], 1.0) for index in range(min(len(src_texts), len(tgt_texts)))]


def test_list_book_chapters_and_chapter_text(tmp_path: Path):
    book = _book(
        "Source",
        "zh",
        [
            ("第一章", "<p>甲。</p><p>乙。</p>"),
            ("附录", "<p>注释。</p>"),
        ],
    )
    path = _write_book(book, tmp_path / "source.epub")
    extraction = api.extract_book(path, language="zh")

    chapters = service.list_book_chapters(extraction)
    assert len(chapters["chapters"]) == 2
    assert chapters["chapters"][0]["chapter_id"]
    assert chapters["chapters"][0]["kind_guess"] == "body"

    chapter_id = chapters["chapters"][0]["chapter_id"]
    text_payload = service.get_chapter_text(extraction, chapter_id, granularity="sentence")
    assert [segment["text"] for segment in text_payload["segments"]] == ["甲。", "乙。"]


def test_search_and_get_segment(tmp_path: Path):
    book = _book(
        "Lookup",
        "zh",
        [("第一章", "<p>这里有关键句子。</p><p>普通句子。</p>")],
    )
    path = _write_book(book, tmp_path / "lookup.epub")
    extraction = api.extract_book(path, language="zh")

    search = service.search_book_text(extraction, "关键")
    assert len(search["matches"]) == 1

    segment = service.get_segment(extraction, search["matches"][0]["segment_id"])
    assert segment["text"] == "这里有关键句子。"
    assert segment["chapter_id"] == search["matches"][0]["chapter_id"]


def test_align_chapter_pair_and_summary(tmp_path: Path):
    source = _book("Source", "zh", [("第一章", "<p>甲。</p><p>乙。</p>")])
    target = _book("Target", "ja", [("第一章", "<p>あ。</p><p>い。</p>")])
    source_extraction = api.extract_book(_write_book(source, tmp_path / "src.epub"), language="zh")
    target_extraction = api.extract_book(_write_book(target, tmp_path / "tgt.epub"), language="ja")

    source_chapter_id = source_extraction.chapters[0].chapter_id
    target_chapter_id = target_extraction.chapters[0].chapter_id
    alignment = service.align_chapter_pair(
        source_extraction,
        target_extraction,
        source_chapter_id,
        target_chapter_id,
        aligner=StubBertalignAdapter(),
    )

    summary = service.get_alignment_summary(alignment)
    assert summary["pair_count"] == 2

    pairs = service.get_aligned_pairs(alignment)
    assert pairs["pairs"][0]["source"][0]["text"] == "甲。"
    assert pairs["pairs"][0]["target"][0]["text"] == "あ。"


def test_resolve_cfi_and_extract_text(tmp_path: Path):
    book = _book("CFI", "zh", [("第一章", "<p>甲。</p><p>乙。</p>")])
    path = _write_book(book, tmp_path / "cfi.epub")
    extraction = api.extract_book(path, language="zh")

    first_segment = extraction.sentence_segments[0]
    resolved = service.resolve_cfi(extraction, first_segment.segment.cfi)
    assert resolved["matched_segments"]

    text = service.extract_text_by_cfi(extraction, first_segment.segment.cfi)
    assert "甲" in text["text"]


def test_preview_and_mixed_content_detection(tmp_path: Path):
    book = _book(
        "Mixed",
        "zh",
        [
            (
                "第一章",
                "<h1>第一章</h1><p>正文一。</p><aside epub:type='footnote'><p>注释甲。</p></aside><nav epub:type='toc'><ol><li>目录残留</li></ol></nav><p>正文二。</p>",
            ),
        ],
    )
    path = _write_book(book, tmp_path / "mixed.epub")
    extraction = api.extract_book(path, language="zh")

    spine = service.preview_spine_documents(extraction)
    assert spine["documents"][0]["file_name"] == "chapter1.xhtml"

    raw = service.preview_document_raw(extraction, 0)
    assert "footnote" in raw["raw_html"]

    rendered = service.preview_document_rendered(extraction, 0, mode="markdown")
    assert "正文一" in rendered["content"]

    headings = service.locate_heading_boundaries(extraction, extraction.chapters[0].chapter_id)
    assert headings["headings"]

    mixed = service.detect_mixed_content_chapters(extraction)
    assert mixed["chapters"][0]["note_like_count"] >= 1


def test_slice_and_split_helpers(tmp_path: Path):
    book = _book(
        "Split",
        "zh",
        [
            (
                "第一章",
                "<p>序。</p><p>第一章</p><p>正文甲。</p><p>第二章</p><p>正文乙。</p><aside epub:type='footnote'><p>注释乙。</p></aside>",
            ),
        ],
    )
    path = _write_book(book, tmp_path / "split.epub")
    extraction = api.extract_book(path, language="zh")
    chapter_id = extraction.chapters[0].chapter_id

    sliced = service.slice_chapter(extraction, chapter_id, 1, 3)
    assert sliced["segment_count"] >= 3

    split = service.split_chapter_by_heading(extraction, chapter_id, headings=["第一章", "第二章"])
    assert len(split["matches"]) >= 2
    assert split["slices"]

    regex_split = service.split_chapter_by_predicate(extraction, chapter_id, rule=r"第二章")
    assert regex_split["matches"][0]["paragraph_idx"] >= 0

    filtered = service.exclude_note_like_segments(extraction, chapter_id)
    assert filtered["removed_segments"]


def test_review_export_and_builder_wrapper(tmp_path: Path):
    source = _book("Source", "zh", [("第一章", "<p>甲。</p><p>乙。</p>")])
    target = _book("Target", "ja", [("第一章", "<p>あ。</p><p>い。</p>")])
    source_extraction = api.extract_book(_write_book(source, tmp_path / "src.epub"), language="zh")
    target_extraction = api.extract_book(_write_book(target, tmp_path / "tgt.epub"), language="ja")

    alignment = service.align_chapter_pair(
        source_extraction,
        target_extraction,
        source_extraction.chapters[0].chapter_id,
        target_extraction.chapters[0].chapter_id,
        aligner=StubBertalignAdapter(),
    )
    review = service.export_review_html(alignment, tmp_path / "review.html")
    assert Path(review["path"]).exists()

    built = service.build_bilingual_epub_from_alignment(
        alignment,
        source_extraction,
        target_extraction,
        tmp_path / "built.epub",
        include_note_appendix=False,
        include_extra_target_appendix=False,
    )
    assert Path(built["path"]).exists()
