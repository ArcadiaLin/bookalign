"""Engineering API tests."""

from pathlib import Path

from ebooklib import epub

from bookalign import (
    extract_book,
    get_chapter_count,
    get_chapter_records,
    list_chapters,
    load_epub,
    load_extraction_json,
    save_extraction_json,
)


def _book(title: str, language: str, chapters: list[tuple[str, str]]) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language(language)

    docs = []
    for idx, (chapter_title, body) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter{idx}.xhtml',
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


def test_extract_book_exposes_chapter_metadata_and_dual_granularity():
    book = _book(
        'Target',
        'zh',
        [
            (
                '目录',
                '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'
                '<p>正文<a class="noteref" href="#note-1">1</a>。</p>'
                '<div class="annotation" id="footnote-1"><p id="note-1">注释正文。</p></div>',
            ),
            ('第一章', '<p>甲。</p><p>乙。</p>'),
        ],
    )

    extraction = extract_book(book, language='zh')
    chapters = list_chapters(extraction)

    assert [chapter.chapter_id for chapter in chapters] == ['目录', '第一章']
    assert chapters[0].is_paratext is True
    assert chapters[0].sentence_count == 3
    assert chapters[0].paragraph_count == 3
    assert chapters[0].alignment_sentence_count == 1
    assert chapters[0].alignment_paragraph_count == 1
    assert extraction.default_granularity == 'sentence'
    assert extraction.sentence_segments[0].granularity == 'sentence'
    assert extraction.paragraph_segments[0].granularity == 'paragraph'
    assert extraction.paragraph_segments[0].segment.sentence_idx is None


def test_extract_book_assigns_unique_chapter_ids_for_duplicate_titles():
    book = _book(
        'Dup',
        'zh',
        [
            ('第一章', '<p>甲。</p>'),
            ('第一章', '<p>乙。</p>'),
        ],
    )

    extraction = extract_book(book, language='zh')

    assert [chapter.chapter_id for chapter in extraction.chapters] == ['第一章', '第一章-2']


def test_get_chapter_records_defaults_to_all_segments_and_supports_filters():
    book = _book(
        'Target',
        'zh',
        [
            (
                '目录',
                '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'
                '<p>正文<a class="noteref" href="#note-1">1</a>。</p>'
                '<div class="annotation" id="footnote-1"><p id="note-1">注释正文。</p></div>',
            ),
        ],
    )

    extraction = extract_book(book, language='zh')

    all_sentence_records = get_chapter_records(extraction, '目录')
    align_sentence_records = get_chapter_records(extraction, '目录', include_retained=False)
    paragraph_records = get_chapter_records(extraction, '目录', granularity='paragraph', limit=2, offset=1)

    assert [record.segment.text for record in all_sentence_records] == ['第一章', '正文1。', '注释正文。']
    assert [record.segment.text for record in align_sentence_records] == ['正文1。']
    assert [record.segment.text for record in paragraph_records] == ['正文1。', '注释正文。']
    assert get_chapter_count(extraction, '目录') == 3
    assert get_chapter_count(extraction, '目录', include_retained=False) == 1
    assert get_chapter_count(extraction, '目录', granularity='paragraph') == 3


def test_extraction_json_round_trip_preserves_records(tmp_path: Path):
    book = _book(
        'Target',
        'zh',
        [
            ('第一章', '<p>甲。</p><p>乙。</p>'),
            ('第二章', '<p>丙。</p>'),
        ],
    )
    extraction = extract_book(book, language='zh', granularity='paragraph')

    path = tmp_path / 'extraction.json'
    save_extraction_json(extraction, path)
    restored = load_extraction_json(path)

    assert restored == extraction


def test_extract_book_reads_epub_path(tmp_path: Path):
    book = _book(
        'PathBook',
        'zh',
        [('第一章', '<p>甲。</p>')],
    )
    path = tmp_path / 'path-book.epub'
    epub.write_epub(str(path), book)

    loaded = load_epub(path)
    extraction = extract_book(path, language='zh')

    assert loaded.get_metadata('DC', 'title')[0][0] == 'PathBook'
    assert extraction.source_path == str(path)
    assert [record.segment.text for record in get_chapter_records(extraction, 0)] == ['甲。']
