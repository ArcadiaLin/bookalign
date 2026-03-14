from __future__ import annotations

import pytest

pytest.importorskip('pysbd')

from bookalign.epub.sentence_splitter import SentenceSplitter


@pytest.mark.parametrize(
    ('language', 'text', 'expected'),
    [
        ('ja', '彼は言った。「そうですね。」そして歩き出した。', ['彼は言った。', '「そうですね。」', 'そして歩き出した。']),
        ('zh', '她问：“你去吗？”我说：“去。”', ['她问：“你去吗？”', '我说：“去。”']),
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
