"""builder tests."""

from pathlib import Path

from ebooklib import epub

from bookalign.epub.builder import build_bilingual_epub
from bookalign.epub.reader import get_spine_documents, read_epub
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
