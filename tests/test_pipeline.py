"""pipeline tests."""

from pathlib import Path

from ebooklib import epub
import pytest

from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.pipeline import (
    align_books,
    extract_sentence_chapters,
    match_extracted_chapters,
    run_bilingual_epub_pipeline,
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
    return book


class StubAligner:
    def __init__(self):
        self.calls = []

    def align(self, src_texts, tgt_texts):
        self.calls.append((src_texts, tgt_texts))
        return [([idx], [idx], 1.0) for idx in range(min(len(src_texts), len(tgt_texts)))]


def test_align_books_extracts_and_aligns_chapters_in_order():
    source_book = _book(
        'Source',
        'zh',
        [
            ('第一章', '<p>甲。</p><p>乙。</p>'),
            ('第二章', '<p>丙。</p>'),
        ],
    )
    target_book = _book(
        'Target',
        'ja',
        [
            ('第一章', '<p>あ。</p><p>い。</p>'),
            ('第二章', '<p>う。</p>'),
        ],
    )
    aligner = StubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='zh',
        target_lang='ja',
        aligner=aligner,
    )

    assert len(aligner.calls) == 2
    assert aligner.calls[0] == (['甲。', '乙。'], ['あ。', 'い。'])
    assert aligner.calls[1] == (['丙。'], ['う。'])
    assert len(result.pairs) == 3
    assert result.pairs[0].source[0].chapter_idx == 0
    assert result.pairs[-1].source[0].chapter_idx == 1


def _paragraphs(count: int, prefix: str) -> str:
    return ''.join(f'<p>{prefix}{idx}。</p>' for idx in range(count))


def test_match_extracted_chapters_skips_front_and_back_matter():
    source_book = _book(
        'Source',
        'ja',
        [
            ('封面', '<p>金閣寺</p>'),
            ('目次', '<p>目次。</p><p>第一章。</p>'),
            ('第一章', _paragraphs(60, '原一')),
            ('第二章', _paragraphs(58, '原二')),
            ('注解', _paragraphs(45, '注')),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('版权', '<p>书籍信息</p>'),
            ('第一章', _paragraphs(57, '译一')),
            ('第二章', _paragraphs(61, '译二')),
            ('后记', '<p>译后记。</p>'),
        ],
    )

    source_chapters = extract_sentence_chapters(source_book, language='ja')
    target_chapters = extract_sentence_chapters(target_book, language='zh')
    matches = match_extracted_chapters(source_chapters, target_chapters)

    assert len(matches) == 2
    assert [match.source_chapter.spine_idx for match in matches] == [2, 3]
    assert [match.target_chapter.spine_idx for match in matches] == [1, 2]


def test_match_extracted_chapters_raw_mode_keeps_paratext_candidates():
    source_book = _book(
        'Source',
        'ja',
        [
            ('封面', '<p>金閣寺</p>'),
            ('第一章', _paragraphs(60, '原一')),
            ('第二章', _paragraphs(58, '原二')),
            ('注解', '<p>注解。</p>'),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('版权', '<p>书籍信息</p>'),
            ('第一章', _paragraphs(57, '译一')),
            ('第二章', _paragraphs(61, '译二')),
            ('后记', '<p>译后记。</p>'),
        ],
    )

    source_chapters = extract_sentence_chapters(source_book, language='ja')
    target_chapters = extract_sentence_chapters(target_book, language='zh')
    matches = match_extracted_chapters(
        source_chapters,
        target_chapters,
        chapter_match_mode='raw',
    )

    assert len(matches) == 4
    assert [match.source_chapter.spine_idx for match in matches] == [0, 1, 2, 3]
    assert [match.target_chapter.spine_idx for match in matches] == [0, 1, 2, 3]


def test_align_books_uses_chapter_matching_before_sentence_alignment():
    source_book = _book(
        'Source',
        'ja',
        [
            ('封面', '<p>金閣寺</p>'),
            ('第一章', '<p>甲。</p><p>乙。</p>'),
            ('第二章', '<p>丙。</p>'),
            ('注解', '<p>参考文献。</p>'),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('版权', '<p>书籍信息</p>'),
            ('第一章', '<p>あ。</p><p>い。</p>'),
            ('第二章', '<p>う。</p>'),
        ],
    )
    aligner = StubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='ja',
        target_lang='zh',
        chapter_match_mode='structured',
        aligner=aligner,
    )

    assert len(aligner.calls) == 2
    assert aligner.calls[0] == (['甲。', '乙。'], ['あ。', 'い。'])
    assert aligner.calls[1] == (['丙。'], ['う。'])
    assert len(result.pairs) == 3


@pytest.mark.integration
def test_match_extracted_chapters_with_real_kinkaku_books():
    source_book = read_epub(Path('books/金閣寺 (三島由紀夫) (Z-Library).epub'))
    target_book = read_epub(Path('books/金阁寺 (三岛由纪夫) (Z-Library).epub'))

    source_chapters = extract_sentence_chapters(source_book, language='ja')
    target_chapters = extract_sentence_chapters(target_book, language='zh')
    matches = match_extracted_chapters(source_chapters, target_chapters)

    assert len(matches) == 10
    assert [match.source_chapter.spine_idx for match in matches] == list(range(5, 15))
    assert [match.target_chapter.spine_idx for match in matches] == list(range(3, 13))


@pytest.mark.integration
def test_run_bilingual_epub_pipeline_with_real_kinkaku_books_uses_matched_body_chapters(
    tmp_path: Path,
):
    output_path = tmp_path / 'kinkaku-aligned.epub'
    aligner = StubAligner()

    result = run_bilingual_epub_pipeline(
        source_epub_path=Path('books/金閣寺 (三島由紀夫) (Z-Library).epub'),
        target_epub_path=Path('books/金阁寺 (三岛由纪夫) (Z-Library).epub'),
        output_path=output_path,
        source_lang='ja',
        target_lang='zh',
        aligner=aligner,
    )

    assert output_path.exists()
    assert len(aligner.calls) == 10
    assert aligner.calls[0][0][0] == '幼時から父は、私によく、金閣のことを語った。'
    assert aligner.calls[0][1][0] == '打小时候起，父亲就常常跟我讲金阁的故事。'
    assert result.pairs

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert len(docs) == 10
    first_doc_html = docs[0][1].get_content().decode('utf-8')
    assert '幼時から父は、私によく、金閣のことを語った。' in first_doc_html
    assert '打小时候起，父亲就常常跟我讲金阁的故事。' in first_doc_html
