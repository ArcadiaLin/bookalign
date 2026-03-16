"""pipeline tests."""

from ebooklib import epub

from bookalign.pipeline import align_books


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
