"""builder tests."""

from pathlib import Path
from zipfile import ZipFile

from ebooklib import epub

from bookalign.epub.builder import (
    build_bilingual_epub,
    build_bilingual_epub_on_source_layout,
)
from bookalign.epub.extractor import extract_segments
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.models.types import AlignedPair, AlignmentResult, Segment


def _book(title: str, language: str, chapter_title: str, body: str) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language(language)

    chapter = epub.EpubHtml(
        title=chapter_title,
        file_name='chapter1.xhtml',
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
        cfi='epubcfi(/6/2)',
        chapter_idx=chapter_idx,
        paragraph_idx=paragraph_idx,
        sentence_idx=sentence_idx,
        paragraph_cfi='epubcfi(/6/2)',
    )


def test_build_bilingual_epub_writes_sentence_level_output(tmp_path: Path):
    source_book = _book('Chinese Source', 'zh', '第一章', '<p>甲。乙。</p>')
    target_book = _book('Japanese Target', 'ja', '第一章', '<p>あ。い。</p>')
    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[_segment('甲。', paragraph_idx=0, sentence_idx=0)],
                target=[_segment('あ。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[_segment('乙。', paragraph_idx=0, sentence_idx=1)],
                target=[_segment('い。', paragraph_idx=0, sentence_idx=1)],
                score=1.0,
            ),
        ],
        source_lang='zh',
        target_lang='ja',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned.epub'
    build_bilingual_epub(alignment, source_book, target_book, output_path)

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert len(docs) == 1

    content = docs[0][1].get_content().decode('utf-8')
    assert 'source-sentence' in content
    assert 'target-sentence' in content
    assert '甲。' in content
    assert 'あ。' in content
    assert '乙。' in content
    assert 'い。' in content


def test_build_bilingual_epub_keeps_target_only_pairs(tmp_path: Path):
    source_book = _book('Chinese Source', 'zh', '第一章', '<p>甲。</p>')
    target_book = _book('Japanese Target', 'ja', '第一章', '<p>あ。</p><p>補句。</p>')
    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[_segment('甲。', paragraph_idx=0, sentence_idx=0)],
                target=[_segment('あ。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[],
                target=[_segment('補句。', paragraph_idx=1, sentence_idx=0)],
                score=0.6,
            ),
        ],
        source_lang='zh',
        target_lang='ja',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-target-only.epub'
    build_bilingual_epub(alignment, source_book, target_book, output_path)

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert len(docs) == 1

    content = docs[0][1].get_content().decode('utf-8')
    assert '補句。' in content
    assert '[原文缺失]' in content


def test_build_bilingual_epub_uses_stable_fallback_chapter_titles(tmp_path: Path):
    source_book = _book('Japanese Source', 'ja', '', '<p>甲。</p>')
    target_book = _book('Chinese Target', 'zh', '', '<p>乙。</p>')
    source_doc = source_book.spine[0]
    target_doc = target_book.spine[0]
    source_doc.file_name = 'xhtml/0004.xhtml'
    target_doc.file_name = 'Text/chapter01.xhtml'

    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[_segment('甲。', paragraph_idx=0, sentence_idx=0)],
                target=[_segment('乙。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-fallback-title.epub'
    build_bilingual_epub(alignment, source_book, target_book, output_path)

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    content = docs[0][1].get_content().decode('utf-8')
    assert '<h1>Chapter 1</h1>' in content


def test_build_bilingual_epub_on_source_layout_injects_translation_blocks(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<div class="chapter"><p><strong>甲。</strong>乙。</p></div>',
    )
    target_book = _book('English Target', 'en', 'Chapter 1', '<p>A. B.</p>')
    chapter = get_spine_documents(source_book)[0][1]
    source_segments = extract_segments(
        source_book,
        chapter,
        chapter_idx=0,
        splitter=SentenceSplitter(language='ja'),
    )

    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[source_segments[0]],
                target=[_segment('A.', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[source_segments[1]],
                target=[_segment('B.', paragraph_idx=0, sentence_idx=1)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='en',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-source-layout.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
    )

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert docs[0][1].get_name() == 'chapter1.xhtml'

    content = docs[0][1].get_content().decode('utf-8')
    assert '<strong>甲。</strong>乙。' in content
    assert 'bookalign-translation-block' not in content
    assert 'data-bookalign-anchor-cfi' not in content
    assert 'A. B.' in content
    assert '<p>A. B.</p>' in content
    assert '<p><br/></p>' in content


def test_build_bilingual_epub_on_source_layout_preserves_toc_titles_and_horizontal_css(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '',
        '<div class="main"><p>甲。</p></div>',
    )
    chapter = source_book.spine[0]
    chapter.title = ''
    chapter.file_name = 'xhtml/0004.xhtml'
    chapter.set_content(
        """<?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml">
          <head>
            <meta charset="UTF-8"/>
            <title>原始标题</title>
            <link rel="stylesheet" type="text/css" href="../style/book-style.css"/>
          </head>
          <body><div class="main"><p>甲。</p></div></body>
        </html>""".encode('utf-8')
    )
    source_book.toc = [epub.Link('xhtml/0004.xhtml', '第　一　章', 'toc1')]
    source_segments = extract_segments(
        source_book,
        chapter,
        chapter_idx=0,
        splitter=SentenceSplitter(language='ja'),
    )

    target_book = _book('Chinese Target', 'zh', '第一章', '<p>乙。</p>')
    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[source_segments[0]],
                target=[_segment('译文。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-source-layout-nav.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
    )

    built = read_epub(output_path)
    assert built.toc
    assert built.direction == 'ltr'
    first_entry = built.toc[0]
    assert getattr(first_entry, 'title', '') == '第　一　章'

    content = get_spine_documents(built)[0][1].get_content().decode('utf-8')
    assert '<p>译文。</p>' in content

    css_items = [
        item for item in built.get_items()
        if getattr(item, 'file_name', '') == 'styles/bookalign-source-layout.css'
    ]
    assert css_items
    css = css_items[0].get_content().decode('utf-8')
    assert 'writing-mode: horizontal-tb' in css
    assert 'text-align: left' in css

    with ZipFile(output_path) as archive:
        raw = archive.read('EPUB/xhtml/0004.xhtml').decode('utf-8')
    assert '../style/book-style.css' in raw
    assert '../styles/bookalign-source-layout.css' in raw
    assert '<p>译文。</p>\n' in raw


def test_build_bilingual_epub_on_source_layout_can_emit_translation_metadata(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<div class="chapter"><p>甲。</p></div>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>译文。</p>')
    chapter = get_spine_documents(source_book)[0][1]
    source_segments = extract_segments(
        source_book,
        chapter,
        chapter_idx=0,
        splitter=SentenceSplitter(language='ja'),
    )

    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[source_segments[0]],
                target=[_segment('译文。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-source-layout-metadata.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        emit_translation_metadata=True,
    )

    content = get_spine_documents(read_epub(output_path))[0][1].get_content().decode('utf-8')
    assert 'bookalign-translation-block' in content
    assert 'data-bookalign-anchor-cfi' in content
