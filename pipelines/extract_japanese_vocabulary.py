"""Extract Japanese vocabulary from an EPUB into a newline-delimited text file."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from bookalign.pipeline import extract_sentence_chapters
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.epub.reader import read_epub


_JAPANESE_CHAR_RE = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff々ヶー]')
_PURE_NUMBER_RE = re.compile(r'^[0-9０-９]+$')
_PURE_SYMBOL_RE = re.compile(r'^[^\w\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff々ヶー]+$')
_SENTENCE_END_RE = re.compile(r'[。！？!?]$')
_PARATEXT_TITLE_RE = re.compile(
    r'(?:'
    r'cover|title|toc|contents|copyright|license|colophon|preface|foreword|'
    r'acknowledg|appendix|index|about|notes?|postscript|afterword|section0+|'
    r'封面|版权|版權|目录|目次|书籍信息|書籍情報|说明|說明|前言|后记|後記|译后记|譯後記|'
    r'附录|附錄|附记|附記|注\s*解|註\s*解|解説|解說|年\s*谱|年\s*譜|'
    r'参考文献|參考文獻|人と文学|について|表紙|奥付|あとがき'
    r')',
    re.IGNORECASE,
)
_ALLOWED_POS = {'名詞', '動詞', '形容詞', '副詞'}
_BLOCKED_SUBPOS = {
    '名詞': {'非自立', '代名詞', '数', '接尾'},
    '動詞': {'非自立', '接尾'},
    '形容詞': {'非自立', '接尾'},
}


@dataclass(frozen=True)
class MeCabToken:
    surface: str
    pos: str
    subpos: str
    base_form: str

    @property
    def vocabulary_form(self) -> str:
        if self.pos in {'動詞', '形容詞'} and self.base_form and self.base_form != '*':
            return self.base_form
        return self.surface


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Extract Japanese vocabulary from an EPUB and write one term per line.',
    )
    parser.add_argument('input_epub', type=Path, help='Input Japanese EPUB path.')
    parser.add_argument('output_txt', type=Path, help='Output TXT path.')
    parser.add_argument(
        '--mecab-bin',
        default='mecab',
        help='MeCab executable path. Default: mecab',
    )
    parser.add_argument(
        '--keep-duplicates',
        action='store_true',
        help='Keep repeated vocabulary instead of de-duplicating by first appearance.',
    )
    return parser


def extract_body_texts(epub_path: Path) -> list[str]:
    """Extract only substantive body text from a Japanese EPUB."""

    book = read_epub(epub_path)
    chapters = extract_sentence_chapters(book, language='ja', extract_mode='filtered_preserve')
    texts: list[str] = []
    for chapter in chapters:
        if _looks_like_paratext_title(chapter.doc.title):
            continue
        for segment in chapter.alignment_segments:
            normalized = SentenceSplitter.normalize_text(segment.text)
            if not normalized:
                continue
            if not _looks_like_body_sentence(normalized):
                continue
            texts.append(normalized)
    return texts


def _looks_like_paratext_title(title: str | None) -> bool:
    normalized = SentenceSplitter.normalize_text(title or '')
    if not normalized:
        return False
    return bool(_PARATEXT_TITLE_RE.search(normalized))


def _looks_like_body_sentence(text: str) -> bool:
    if _SENTENCE_END_RE.search(text):
        return True
    return len(text) >= 20


def run_mecab(text: str, *, mecab_bin: str = 'mecab') -> list[MeCabToken]:
    """Tokenize text with MeCab and return parsed tokens."""

    result = subprocess.run(
        [mecab_bin],
        input=text,
        capture_output=True,
        text=True,
        check=True,
    )
    return parse_mecab_output(result.stdout)


def parse_mecab_output(stdout: str) -> list[MeCabToken]:
    """Parse default MeCab output into token records."""

    tokens: list[MeCabToken] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or line == 'EOS' or '\t' not in line:
            continue
        surface, feature_text = line.split('\t', 1)
        features = [field.strip() for field in feature_text.split(',')]
        pos = features[0] if len(features) > 0 else ''
        subpos = features[1] if len(features) > 1 else ''
        base_form = features[6] if len(features) > 6 else surface
        tokens.append(
            MeCabToken(
                surface=surface,
                pos=pos,
                subpos=subpos,
                base_form=base_form,
            )
        )
    return tokens


def select_vocabulary(tokens: list[MeCabToken], *, keep_duplicates: bool = False) -> list[str]:
    """Filter MeCab tokens down to a clean vocabulary list."""

    vocabulary: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token.pos not in _ALLOWED_POS:
            continue
        if token.subpos in _BLOCKED_SUBPOS.get(token.pos, set()):
            continue

        word = token.vocabulary_form.strip()
        if not word or word == '*':
            continue
        if _PURE_NUMBER_RE.fullmatch(word):
            continue
        if _PURE_SYMBOL_RE.fullmatch(word):
            continue
        if not _JAPANESE_CHAR_RE.search(word):
            continue

        if keep_duplicates:
            vocabulary.append(word)
            continue
        if word in seen:
            continue
        seen.add(word)
        vocabulary.append(word)
    return vocabulary


def extract_vocabulary_from_epub(
    epub_path: Path,
    *,
    mecab_bin: str = 'mecab',
    keep_duplicates: bool = False,
) -> list[str]:
    """Extract vocabulary from an EPUB in reading order."""

    texts = extract_body_texts(epub_path)
    if not texts:
        return []
    tokens = run_mecab('\n'.join(texts), mecab_bin=mecab_bin)
    return select_vocabulary(tokens, keep_duplicates=keep_duplicates)


def write_vocabulary_txt(words: list[str], output_path: Path) -> None:
    """Write vocabulary as newline-delimited UTF-8 text."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = '\n'.join(words)
    if content:
        content = f'{content}\n'
    output_path.write_text(content, encoding='utf-8')


def main() -> None:
    args = build_parser().parse_args()
    words = extract_vocabulary_from_epub(
        args.input_epub,
        mecab_bin=args.mecab_bin,
        keep_duplicates=args.keep_duplicates,
    )
    write_vocabulary_txt(words, args.output_txt)


if __name__ == '__main__':
    main()
