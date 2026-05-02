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

from epub.builder import _collect_runtime_text_spans, build_bilingual_epub, build_bilingual_epub_on_source_layout  # noqa: E402
from epub.extractor import _collect_text_spans, extract_segments  # noqa: E402
from epub.reader import get_spine_documents, read_epub  # noqa: E402
from epub.sentence_splitter import SentenceSplitter  # noqa: E402
from epub.tag_filters import build_tag_filter_config  # noqa: E402
from models.types import AlignedPair, AlignmentResult, Segment  # noqa: E402


def _book(title: str, language: str, chapter_title: str, body: str) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language(language)

    chapter = epub.EpubHtml(
        title=chapter_title,
        file_name="chapter1.xhtml",
        lang=language,
    )
    chapter.set_content(body)
    book.add_item(chapter)
    book.spine = [chapter]
    book.toc = (chapter,)
    return book


def _segment(text: str, *, chapter_idx: int = 0, paragraph_idx: int = 0, sentence_idx: int = 0) -> Segment:
    return Segment(
        text=text,
        cfi="epubcfi(/6/2)",
        chapter_idx=chapter_idx,
        paragraph_idx=paragraph_idx,
        sentence_idx=sentence_idx,
        paragraph_cfi="epubcfi(/6/2)",
    )


def test_runtime_span_collection_reuses_extractor_normalization():
    book = _book(
        "Source",
        "ja",
        "第一章",
        "<p>甲<ruby>漢<rt>kan</rt>字</ruby><span>works.</span><span>Despite</span><br/>乙</p>",
    )
    chapter = get_spine_documents(book)[0][1]

    from epub.cfi import parse_item_xml  # noqa: E402

    xml_root = parse_item_xml(chapter)
    paragraph = xml_root.xpath('.//*[local-name()="p"]')[0]
    config = build_tag_filter_config("filtered_preserve")

    collected = _collect_text_spans(paragraph, xml_root.getroottree(), config)
    runtime = _collect_runtime_text_spans(paragraph, config)

    assert [span.text for span in runtime] == [span.text for span in collected]


def test_source_layout_builder_still_injects_translation_blocks(tmp_path: Path):
    source_book = _book(
        "Japanese Source",
        "ja",
        "第一章",
        "<div class='chapter'><p><strong>甲。</strong>乙。</p></div>",
    )
    target_book = _book("English Target", "en", "Chapter 1", "<p>A. B.</p>")
    chapter = get_spine_documents(source_book)[0][1]
    source_segments = extract_segments(
        source_book,
        chapter,
        chapter_idx=0,
        splitter=SentenceSplitter(language="ja"),
    )

    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[source_segments[0]],
                target=[_segment("A.", paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[source_segments[1]],
                target=[_segment("B.", paragraph_idx=0, sentence_idx=1)],
                score=1.0,
            ),
        ],
        source_lang="ja",
        target_lang="en",
        granularity="sentence",
    )

    output_path = tmp_path / "aligned-source-layout.epub"
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        emit_translation_metadata=True,
    )

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    content = docs[0][1].get_content().decode("utf-8")
    assert "bookalign-translation-block" in content
    assert "A. B." in content
    assert "<strong>甲。</strong>" in content


def test_source_layout_builder_indents_chinese_translation_blocks_by_default(tmp_path: Path):
    source_book = _book(
        "Japanese Source",
        "ja",
        "第一章",
        "<div class='chapter'><p>甲。</p></div>",
    )
    target_book = _book("Chinese Target", "zh", "第一章", "<p>这是译文。</p>")
    chapter = get_spine_documents(source_book)[0][1]
    source_segments = extract_segments(
        source_book,
        chapter,
        chapter_idx=0,
        splitter=SentenceSplitter(language="ja"),
    )

    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[source_segments[0]],
                target=[_segment("这是译文。", paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang="ja",
        target_lang="zh",
        granularity="sentence",
    )

    output_path = tmp_path / "aligned-source-layout-zh.epub"
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        emit_translation_metadata=True,
    )

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    content = docs[0][1].get_content().decode("utf-8")
    assert ">  这是译文。<" in content


def test_generated_bilingual_epub_indents_chinese_target_paragraphs_by_default(tmp_path: Path):
    source_book = _book("Source", "ja", "第一章", "<p>甲。</p>")
    target_book = _book("Target", "zh", "第一章", "<p>这是译文。</p>")
    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[_segment("甲。", chapter_idx=0, paragraph_idx=0, sentence_idx=0)],
                target=[_segment("这是译文。", chapter_idx=0, paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang="ja",
        target_lang="zh",
        granularity="sentence",
    )

    output_path = tmp_path / "generated-bilingual-zh.epub"
    build_bilingual_epub(
        alignment,
        source_book,
        target_book,
        output_path,
    )

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    content = docs[0][1].get_content().decode("utf-8")
    assert ">  这是译文。<" in content
