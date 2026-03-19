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
from bookalign.models.types import AlignedPair, AlignmentResult, JumpFragment, Segment


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


def _segment_with_jump(
    text: str,
    *,
    href: str = '',
    anchor_id: str = '',
    is_note_like: bool = False,
    chapter_idx: int = 0,
    paragraph_idx: int = 0,
    sentence_idx: int = 0,
) -> Segment:
    fragments = []
    if href:
        fragments.append(JumpFragment(kind='href', text='1', start=max(0, len(text) - 1), end=len(text), href=href))
    if anchor_id:
        fragments.append(JumpFragment(kind='id', anchor_id=anchor_id))
    return Segment(
        text=text,
        cfi='epubcfi(/6/2)',
        chapter_idx=chapter_idx,
        paragraph_idx=paragraph_idx,
        sentence_idx=sentence_idx,
        paragraph_cfi='epubcfi(/6/2)',
        has_jump_markup=bool(fragments),
        is_note_like=is_note_like,
        jump_fragments=fragments,
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


def test_build_bilingual_epub_on_source_layout_inline_rewrites_source_block(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<p><ruby>甲<rt>こう</rt></ruby>乙。</p><p><strong>丙。</strong></p>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>译一。译二。</p>')
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
                target=[_segment('译一。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[source_segments[1]],
                target=[_segment('译二。', paragraph_idx=0, sentence_idx=1)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-source-layout-inline.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        writeback_mode='inline',
    )

    built = read_epub(output_path)
    assert built.direction == 'ltr'
    content = get_spine_documents(built)[0][1].get_content().decode('utf-8')
    assert 'bookalign-translation-block' not in content
    assert '<ruby>甲<rt>こう</rt></ruby>乙。' in content
    assert '<strong>丙。</strong>' in content
    assert '译一。' in content
    assert '译二。' in content
    assert content.count('<p><br/></p>') == 2

    with ZipFile(output_path) as archive:
        raw = archive.read('EPUB/chapter1.xhtml').decode('utf-8')
    assert '<br/>' in raw
    assert '译一。' in raw
    assert '译二。' in raw


def test_inline_writeback_reuses_trimmed_runtime_coordinates(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<p>　甲。乙。</p>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>译一。译二。</p>')
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
                target=[_segment('译一。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[source_segments[1]],
                target=[_segment('译二。', paragraph_idx=0, sentence_idx=1)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-inline-trimmed.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        writeback_mode='inline',
    )

    with ZipFile(output_path) as archive:
        raw = archive.read('EPUB/chapter1.xhtml').decode('utf-8').replace('\n', '')
    assert '甲。<br/>译一。<br/>乙。<br/>译二。' in raw


def test_source_layout_normalizes_vertical_punctuation_for_horizontal_chinese_output(tmp_path: Path):
    def make_fixture() -> tuple[epub.EpubBook, epub.EpubBook, AlignmentResult]:
        source_book = _book(
            'Japanese Source',
            'ja',
            '第一章',
            '<p>甲。</p>',
        )
        target_book = _book('Chinese Target', 'zh', '第一章', '<p>︽告白︾﹁真的嗎﹂︿上卷﹀</p>')
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
                    target=[_segment('︽告白︾﹁真的嗎﹂︿上卷﹀', paragraph_idx=0, sentence_idx=0)],
                    score=1.0,
                ),
            ],
            source_lang='ja',
            target_lang='zh',
            granularity='sentence',
        )
        return source_book, target_book, alignment

    source_book, target_book, alignment = make_fixture()
    paragraph_output = tmp_path / 'aligned-vertical-punct-paragraph.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        paragraph_output,
        writeback_mode='paragraph',
    )
    paragraph_content = get_spine_documents(read_epub(paragraph_output))[0][1].get_content().decode('utf-8')
    assert '《告白》「真的嗎」〈上卷〉' in paragraph_content

    source_book, target_book, alignment = make_fixture()
    inline_output = tmp_path / 'aligned-vertical-punct-inline.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        inline_output,
        writeback_mode='inline',
    )
    inline_content = get_spine_documents(read_epub(inline_output))[0][1].get_content().decode('utf-8')
    assert '《告白》「真的嗎」〈上卷〉' in inline_content


def test_source_layout_can_disable_vertical_punctuation_normalization(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<p>甲。</p>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>︽告白︾</p>')
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
                target=[_segment('︽告白︾', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-vertical-punct-disabled.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        normalize_vertical_punctuation=False,
    )

    content = get_spine_documents(read_epub(output_path))[0][1].get_content().decode('utf-8')
    assert '︽告白︾' in content


def test_full_text_paragraph_writeback_preserves_jump_links_and_appends_unmatched_notes(tmp_path: Path):
    source_book = _book('Japanese Source', 'ja', '第一章', '<p>甲。</p><p>乙。</p>')
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>译文1。</p><p>注释。</p>')
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
                target=[_segment_with_jump('正文1', href='#note-1', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[],
                target=[_segment_with_jump('注释1', anchor_id='note-1', is_note_like=True, paragraph_idx=1, sentence_idx=0)],
                score=0.8,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-full-text-paragraph.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        extract_mode='full_text',
    )

    content = get_spine_documents(read_epub(output_path))[0][1].get_content().decode('utf-8')
    assert 'href="#bookalign-note-0001"' in content
    assert 'id="bookalign-note-0001"' in content
    assert '译注附录' in content


def test_full_text_inline_writeback_preserves_jump_links(tmp_path: Path):
    source_book = _book('Japanese Source', 'ja', '第一章', '<p>甲。</p>')
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>正文1。</p>')
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
                target=[_segment_with_jump('正文1', href='#note-1', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
            AlignedPair(
                source=[],
                target=[_segment_with_jump('注释1', anchor_id='note-1', is_note_like=True, paragraph_idx=1, sentence_idx=0)],
                score=0.6,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-full-text-inline.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        writeback_mode='inline',
        extract_mode='full_text',
    )

    content = get_spine_documents(read_epub(output_path))[0][1].get_content().decode('utf-8')
    assert 'href="#bookalign-note-0001"' in content
    assert 'id="bookalign-note-0001"' in content


def test_filtered_preserve_creates_retained_appendix_and_rewrites_note_links(tmp_path: Path):
    source_book = _book('Japanese Source', 'ja', '第一章', '<p>甲。</p>')
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>正文1。</p><aside epub:type="footnote"><p id="note-1">注释︵一︶。</p></aside>')
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
                target=[_segment_with_jump('正文1', href='#note-1', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
        extract_mode='filtered_preserve',
        retained_target_segments=[
            Segment(
                text='注释︵一︶。',
                cfi='epubcfi(/6/4)',
                chapter_idx=0,
                paragraph_idx=1,
                sentence_idx=0,
                paragraph_cfi='epubcfi(/6/4)',
                raw_html='<p id="note-1">注释︵一︶。</p>',
                has_jump_markup=True,
                is_note_like=True,
                alignment_role='retain',
                paratext_kind='note_body',
                filter_reason='note_block',
                jump_fragments=[JumpFragment(kind='id', anchor_id='note-1')],
            )
        ],
    )

    output_path = tmp_path / 'aligned-filtered-preserve.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
        extract_mode='filtered_preserve',
    )

    built = read_epub(output_path)
    docs = get_spine_documents(built)
    assert len(docs) == 2

    chapter_content = docs[0][1].get_content().decode('utf-8')
    appendix_content = docs[1][1].get_content().decode('utf-8')
    assert 'bookalign-retained-target.xhtml#bookalign-note-0001' in chapter_content
    assert '译文附录' in appendix_content
    assert 'id="bookalign-note-0001"' in appendix_content
    assert '注释（一）。' in appendix_content


def test_vertical_punctuation_normalization_includes_parentheses(tmp_path: Path):
    source_book = _book('Japanese Source', 'ja', '第一章', '<p>甲。</p>')
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>乙。</p>')
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
                target=[_segment('︵注︶', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    output_path = tmp_path / 'aligned-parentheses.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        output_path,
    )

    content = get_spine_documents(read_epub(output_path))[0][1].get_content().decode('utf-8')
    assert '（注）' in content


def test_source_layout_anchors_cross_paragraph_pair_to_last_source_sentence(tmp_path: Path):
    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<p>前句。</p><p>后句。</p>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>合并译文。</p>')
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
                source=[source_segments[0], source_segments[1]],
                target=[_segment('合并译文。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    paragraph_output = tmp_path / 'cross-paragraph-anchor-paragraph.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        paragraph_output,
        writeback_mode='paragraph',
    )
    paragraph_content = get_spine_documents(read_epub(paragraph_output))[0][1].get_content().decode('utf-8')
    assert '<p>前句。</p>' in paragraph_content
    assert '<p>后句。</p>' in paragraph_content
    assert paragraph_content.index('<p>后句。</p>') < paragraph_content.index('<p>合并译文。</p>')

    source_book = _book(
        'Japanese Source',
        'ja',
        '第一章',
        '<p>前句。</p><p>后句。</p>',
    )
    target_book = _book('Chinese Target', 'zh', '第一章', '<p>合并译文。</p>')
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
                source=[source_segments[0], source_segments[1]],
                target=[_segment('合并译文。', paragraph_idx=0, sentence_idx=0)],
                score=1.0,
            ),
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
    )

    inline_output = tmp_path / 'cross-paragraph-anchor-inline.epub'
    build_bilingual_epub_on_source_layout(
        alignment,
        source_book,
        target_book,
        inline_output,
        writeback_mode='inline',
    )
    inline_content = get_spine_documents(read_epub(inline_output))[0][1].get_content().decode('utf-8')
    assert '<p>前句。</p>' in inline_content
    assert '后句。<br/>合并译文。' in inline_content
