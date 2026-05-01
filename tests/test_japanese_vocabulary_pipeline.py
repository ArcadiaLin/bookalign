from pathlib import Path

from ebooklib import epub

from pipelines.extract_japanese_vocabulary import (
    extract_body_texts,
    extract_vocabulary_from_epub,
    parse_mecab_output,
    select_vocabulary,
    write_vocabulary_txt,
)


def _book(title: str, chapters: list[tuple[str, str]]) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language('ja')

    docs = []
    for idx, (chapter_title, body) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapter{idx}.xhtml',
            lang='ja',
        )
        chapter.set_content(body)
        book.add_item(chapter)
        docs.append(chapter)

    book.spine = docs
    book.toc = tuple(docs)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    return book


def test_extract_body_texts_keeps_only_alignment_segments(tmp_path: Path):
    book = _book(
        '金閣寺',
        [
            (
                '第一章',
                '<nav class="toc"><ol><li><a href="#c1">第一章</a></li></ol></nav>'
                '<p>金閣寺の天気はよかった。</p>'
                '<aside epub:type="footnote"><p id="note-1">注釈本文。</p></aside>'
                '<p>幼時に見た。</p>',
            ),
            (
                '年譜',
                '<p>三島由紀夫</p>'
                '<p>田中美代子</p>',
            ),
        ],
    )
    input_path = tmp_path / 'kinkaku.epub'
    epub.write_epub(str(input_path), book)

    texts = extract_body_texts(input_path)

    assert texts == ['金閣寺の天気はよかった。', '幼時に見た。']


def test_select_vocabulary_filters_noise_and_keeps_ordered_unique_terms():
    stdout = """\
金閣寺\t名詞,固有名詞,組織,*,*,*,金閣寺,キンカクジ,キンカクジ
の\t助詞,連体化,*,*,*,*,の,ノ,ノ
天気\t名詞,一般,*,*,*,*,天気,テンキ,テンキ
は\t助詞,係助詞,*,*,*,*,は,ハ,ワ
よかっ\t形容詞,自立,*,*,形容詞・アウオ段,連用タ接続,よい,ヨカッ,ヨカッ
た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
幼時\t名詞,一般,*,*,*,*,幼時,ヨウジ,ヨージ
に\t助詞,格助詞,一般,*,*,*,に,ニ,ニ
見\t動詞,自立,*,*,一段,連用形,見る,ミ,ミ
た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
金閣寺\t名詞,固有名詞,組織,*,*,*,金閣寺,キンカクジ,キンカクジ
。\t記号,句点,*,*,*,*,。,。,。
EOS
"""

    words = select_vocabulary(parse_mecab_output(stdout))

    assert words == ['金閣寺', '天気', 'よい', '幼時', '見る']


def test_extract_vocabulary_from_epub_writes_newline_delimited_txt(tmp_path: Path, monkeypatch):
    book = _book(
        '金閣寺',
        [
            ('第一章', '<p>金閣寺の天気はよかった。</p><p>幼時に見た。</p>'),
        ],
    )
    input_path = tmp_path / 'kinkaku.epub'
    output_path = tmp_path / 'vocab.txt'
    epub.write_epub(str(input_path), book)

    def _fake_run_mecab(text: str, *, mecab_bin: str = 'mecab'):
        assert '金閣寺の天気はよかった。' in text
        assert '幼時に見た。' in text
        return parse_mecab_output(
            """\
金閣寺\t名詞,固有名詞,組織,*,*,*,金閣寺,キンカクジ,キンカクジ
天気\t名詞,一般,*,*,*,*,天気,テンキ,テンキ
幼時\t名詞,一般,*,*,*,*,幼時,ヨウジ,ヨージ
EOS
"""
        )

    monkeypatch.setattr('pipelines.extract_japanese_vocabulary.run_mecab', _fake_run_mecab)

    words = extract_vocabulary_from_epub(input_path)
    write_vocabulary_txt(words, output_path)

    assert words == ['金閣寺', '天気', '幼時']
    assert output_path.read_text(encoding='utf-8') == '金閣寺\n天気\n幼時\n'
