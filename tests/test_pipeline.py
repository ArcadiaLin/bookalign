"""pipeline tests."""

from pathlib import Path

from ebooklib import epub
import pytest

from bookalign.alignment_json import load_alignment_result
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.pipeline import (
    align_books,
    build_bilingual_epub_from_alignment_json,
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
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    return book


class StubAligner:
    def __init__(self):
        self.calls = []

    def align(self, src_texts, tgt_texts):
        self.calls.append((src_texts, tgt_texts))
        return [([idx], [idx], 1.0) for idx in range(min(len(src_texts), len(tgt_texts)))]


class LocalRealignStubAligner:
    def __init__(self):
        self.calls = []

    def align(self, src_texts, tgt_texts):
        self.calls.append((src_texts, tgt_texts))
        if len(self.calls) == 1:
            return [
                ([0], [0], 1.0),
                ([1], [1], 1.0),
                ([2], [2], 1.0),
                ([3, 4, 5, 6], [3], 1.0),
                ([7], [], 1.0),
                ([8, 9, 10, 11], [4], 1.0),
                ([], [5, 6, 7, 8, 9, 10, 11], 1.0),
            ]
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


def test_match_extracted_chapters_skips_structural_frontmatter_before_numbered_sequence():
    source_book = _book(
        'Source',
        'en',
        [
            ('Essay', _paragraphs(45, '前言')),
            ('CHAPTER I', _paragraphs(60, '原一')),
            ('CHAPTER II', _paragraphs(58, '原二')),
            ('CHAPTER III', _paragraphs(55, '原三')),
            ('CHAPTER IV', _paragraphs(57, '原四')),
            ('CHAPTER V', _paragraphs(59, '原五')),
            ('Afterword', _paragraphs(32, '附')),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('希望在人间', _paragraphs(52, '导言')),
            ('第一章', _paragraphs(61, '译一')),
            ('第二章', _paragraphs(57, '译二')),
            ('第三章', _paragraphs(56, '译三')),
            ('第四章', _paragraphs(60, '译四')),
            ('第五章', _paragraphs(58, '译五')),
            ('译后记', _paragraphs(28, '后记')),
        ],
    )

    source_chapters = extract_sentence_chapters(source_book, language='en')
    target_chapters = extract_sentence_chapters(target_book, language='zh')
    matches = match_extracted_chapters(source_chapters, target_chapters)

    assert len(matches) == 5
    assert [match.source_chapter.spine_idx for match in matches] == [1, 2, 3, 4, 5]
    assert [match.target_chapter.spine_idx for match in matches] == [1, 2, 3, 4, 5]


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


def test_extract_sentence_chapters_filtered_preserve_keeps_toc_and_notes():
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

    chapters = extract_sentence_chapters(book, language='zh', extract_mode='filtered_preserve')

    assert len(chapters) == 1
    assert [segment.text for segment in chapters[0].segments][:3] == ['第一章', '正文1。', '注释正文。']


def test_extract_sentence_chapters_filtered_preserve_splits_alignment_and_retained_segments():
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

    chapters = extract_sentence_chapters(book, language='zh', extract_mode='filtered_preserve')

    assert len(chapters) == 1
    assert [segment.text for segment in chapters[0].segments] == ['第一章', '正文1。', '注释正文。']
    assert [segment.text for segment in chapters[0].alignment_segments] == ['正文1。']
    assert [segment.text for segment in chapters[0].retained_segments] == ['第一章', '注释正文。']


def test_align_books_filtered_preserve_defaults_to_structured_chapter_matching():
    source_book = _book(
        'Source',
        'ja',
        [
            ('目次', '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'),
            ('第一章', '<p>甲。</p>'),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('目录', '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'),
            ('第一章', '<p>乙。</p>'),
        ],
    )
    aligner = StubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='ja',
        target_lang='zh',
        extract_mode='filtered_preserve',
        aligner=aligner,
    )

    assert len(aligner.calls) == 1
    assert aligner.calls[0] == (['甲。'], ['乙。'])
    assert result.pairs


def test_align_books_filtered_preserve_aligns_only_body_and_retains_paratext():
    source_book = _book(
        'Source',
        'ja',
        [
            (
                '第一章',
                '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav><p>甲。</p>',
            ),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            (
                '第一章',
                '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'
                '<p>乙<a class="noteref" href="#note-1">1</a>。</p>'
                '<aside epub:type="footnote"><p id="note-1">注释正文。</p></aside>',
            ),
        ],
    )
    aligner = StubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='ja',
        target_lang='zh',
        extract_mode='filtered_preserve',
        aligner=aligner,
    )

    assert len(aligner.calls) == 1
    assert aligner.calls[0] == (['甲。'], ['乙1。'])
    assert [segment.text for segment in result.retained_target_segments] == ['第一章', '注释正文。']
    assert result.extract_mode == 'filtered_preserve'


def test_align_books_retains_unmatched_target_chapter_body_segments():
    source_book = _book(
        'Source',
        'ja',
        [
            ('第一章', '<p>甲。</p>'),
        ],
    )
    target_book = _book(
        'Target',
        'zh',
        [
            ('第一章', '<p>乙。</p>'),
            ('译后记', '<p>这是译后记正文。</p><p>补充说明。</p>'),
        ],
    )
    aligner = StubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='ja',
        target_lang='zh',
        extract_mode='filtered_preserve',
        aligner=aligner,
    )

    assert len(aligner.calls) == 1
    assert aligner.calls[0] == (['甲。'], ['乙。'])
    assert [segment.text for segment in result.retained_target_segments] == ['这是译后记正文。', '补充说明。']
    assert all(segment.alignment_role == 'retain' for segment in result.retained_target_segments)
    assert all(segment.filter_reason == 'unmatched_target_chapter' for segment in result.retained_target_segments)


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


def test_align_books_can_locally_realign_suspect_windows():
    source_book = _book(
        'Source',
        'ja',
        [('第一章', _paragraphs(12, '原'))],
    )
    target_book = _book(
        'Target',
        'zh',
        [('第一章', _paragraphs(12, '译'))],
    )
    aligner = LocalRealignStubAligner()

    result = align_books(
        source_book,
        target_book,
        source_lang='ja',
        target_lang='zh',
        extract_mode='filtered_preserve',
        aligner=aligner,
        enable_local_realign=True,
    )

    assert len(aligner.calls) >= 2
    assert all(len(pair.source) == 1 and len(pair.target) == 1 for pair in result.pairs)
    assert len(result.pairs) >= 11


def test_run_bilingual_epub_pipeline_can_save_alignment_json(tmp_path: Path):
    source_book = _book('Source', 'ja', [('第一章', '<p>甲。</p><p>乙。</p>')])
    target_book = _book('Target', 'zh', [('第一章', '<p>译甲。</p><p>译乙。</p>')])
    source_path = tmp_path / 'source.epub'
    target_path = tmp_path / 'target.epub'
    output_path = tmp_path / 'out.epub'
    json_path = tmp_path / 'alignment.json'
    epub.write_epub(str(source_path), source_book)
    epub.write_epub(str(target_path), target_book)
    aligner = StubAligner()

    result = run_bilingual_epub_pipeline(
        source_epub_path=source_path,
        target_epub_path=target_path,
        output_path=output_path,
        source_lang='ja',
        target_lang='zh',
        alignment_json_output_path=json_path,
        aligner=aligner,
    )

    assert output_path.exists()
    assert json_path.exists()
    assert len(aligner.calls) == 1
    restored = load_alignment_result(json_path)
    assert restored == result


def test_run_bilingual_epub_pipeline_can_build_from_alignment_json_without_aligner(tmp_path: Path):
    source_book = _book('Source', 'ja', [('第一章', '<p>甲。</p><p>乙。</p>')])
    target_book = _book('Target', 'zh', [('第一章', '<p>译甲。</p><p>译乙。</p>')])
    source_path = tmp_path / 'source.epub'
    target_path = tmp_path / 'target.epub'
    json_path = tmp_path / 'alignment.json'
    output_path = tmp_path / 'from-json.epub'
    epub.write_epub(str(source_path), source_book)
    epub.write_epub(str(target_path), target_book)

    seed_aligner = StubAligner()
    seeded = run_bilingual_epub_pipeline(
        source_epub_path=source_path,
        target_epub_path=target_path,
        output_path=tmp_path / 'seed.epub',
        source_lang='ja',
        target_lang='zh',
        alignment_json_output_path=json_path,
        aligner=seed_aligner,
    )
    assert seeded.pairs

    unused_aligner = StubAligner()
    restored = run_bilingual_epub_pipeline(
        source_epub_path=source_path,
        target_epub_path=target_path,
        output_path=output_path,
        source_lang='ja',
        target_lang='zh',
        alignment_json_input_path=json_path,
        aligner=unused_aligner,
    )

    assert output_path.exists()
    assert restored == seeded
    assert unused_aligner.calls == []


def test_build_bilingual_epub_from_alignment_json_reuses_saved_alignment(tmp_path: Path):
    source_book = _book('Source', 'ja', [('第一章', '<p>甲。</p>')])
    target_book = _book('Target', 'zh', [('第一章', '<p>译甲。</p>')])
    source_path = tmp_path / 'source.epub'
    target_path = tmp_path / 'target.epub'
    json_path = tmp_path / 'alignment.json'
    output_path = tmp_path / 'rebuilt.epub'
    epub.write_epub(str(source_path), source_book)
    epub.write_epub(str(target_path), target_book)

    run_bilingual_epub_pipeline(
        source_epub_path=source_path,
        target_epub_path=target_path,
        output_path=tmp_path / 'seed.epub',
        source_lang='ja',
        target_lang='zh',
        alignment_json_output_path=json_path,
        aligner=StubAligner(),
    )

    result = build_bilingual_epub_from_alignment_json(
        source_epub_path=source_path,
        target_epub_path=target_path,
        alignment_json_path=json_path,
        output_path=output_path,
        builder_mode='source_layout',
        writeback_mode='paragraph',
        layout_direction='horizontal',
    )

    assert result.pairs
    assert output_path.exists()


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
    assert aligner.calls[0][0][0] == '幼時から父は、私によく、金閣＊一のことを語った。'
    assert aligner.calls[0][1][0] == '打小时候起，父亲就常常跟我讲金阁的故事。'
    assert result.pairs

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert len(docs) == 10
    first_doc_html = docs[0][1].get_content().decode('utf-8')
    assert '幼時から父は、私によく、金閣＊一のことを語った。' in first_doc_html
    assert '打小时候起，父亲就常常跟我讲金阁的故事。' in first_doc_html
