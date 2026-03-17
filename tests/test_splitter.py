from __future__ import annotations

import pytest

pytest.importorskip('pysbd')

from bookalign.epub.sentence_splitter import SentenceSplitter


@pytest.mark.parametrize(
    ('language', 'text', 'expected'),
    [
        ('ja', '彼は言った。「そうですね。」そして歩き出した。', ['彼は言った。', '「そうですね。」', 'そして歩き出した。']),
        ('zh', '她问：“你去吗？”我说：“去。”', ['她问：“你去吗？”', '我说：“去。”']),
        ('zh', '主治醫生來了說，﹁不敢保證救得活。﹂我像針插包似的被注射樟腦液和葡萄糖。', ['主治醫生來了說，﹁不敢保證救得活。﹂', '我像針插包似的被注射樟腦液和葡萄糖。']),
        ('en', 'Mr. Holmes was not amused. He left at once.', ['Mr. Holmes was not amused.', 'He left at once.']),
        ('es', '¿Vienes conmigo? Claro que sí.', ['¿Vienes conmigo?', 'Claro que sí.']),
    ],
)
def test_sentence_splitter_handles_core_languages(language, text, expected):
    splitter = SentenceSplitter(language)
    assert splitter.split(text) == expected


@pytest.mark.parametrize(
    'text',
    [
        '  A  line \n with\tspaces. Another sentence.  ',
        '\u3000彼は来た。　そして帰った。 ',
    ],
)
def test_sentence_splitter_rejoins_to_normalized_text(text):
    splitter = SentenceSplitter('en')
    normalized = SentenceSplitter.normalize_text(text)
    sentences = splitter.split(text)
    assert SentenceSplitter.normalize_text(' '.join(sentences)) == normalized


def test_cjk_tail_is_attached_without_inserting_space():
    splitter = SentenceSplitter('ja')
    text = '本能寺は天正十年の兵火に焼かれた。……'
    assert splitter.split(text) == ['本能寺は天正十年の兵火に焼かれた。……']


def test_cjk_dialogue_inside_quotes_is_not_oversplit():
    splitter = SentenceSplitter('zh')
    text = '时光机却紧急传来了信息：“嘀！警报警报！有入侵者正试图解体———————”'
    assert splitter.split(text) == ['时光机却紧急传来了信息：“嘀！警报警报！有入侵者正试图解体———————”']


def test_traditional_chinese_nested_compatibility_quotes_are_kept_with_sentence_end():
    splitter = SentenceSplitter('zh')
    text = '他想，﹁這簡直像﹃奇蹟﹄一樣。﹂但沒有人回答。'
    assert splitter.split(text) == ['他想，﹁這簡直像﹃奇蹟﹄一樣。﹂', '但沒有人回答。']


def test_traditional_compatibility_book_title_and_brackets_do_not_split_off_closers():
    splitter = SentenceSplitter('zh')
    text = '他念到︽春琴抄︾。︵未完︶又沉默了。'
    assert splitter.split(text) == ['他念到︽春琴抄︾。', '︵未完︶又沉默了。']


def test_latin_dialogue_tag_is_merged_back():
    splitter = SentenceSplitter('en')
    text = '"Stop!" said Alice.'
    assert splitter.split(text) == ['"Stop!" said Alice.']


def test_latin_colon_lead_in_is_merged_with_quote():
    splitter = SentenceSplitter('es')
    text = 'Le dijo: "Ven conmigo."'
    assert splitter.split(text) == ['Le dijo: "Ven conmigo."']
