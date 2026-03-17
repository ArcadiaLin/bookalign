"""Language-aware sentence splitting for EPUB extracted text."""

from __future__ import annotations

import re


_CJK_STOP_PUNCT = {'。', '！', '？', '!', '?'}
_CJK_CLOSERS = {
    '」', '』', '）', ')', '】', '》', '"', "'", '’', '”',
    '﹂', '﹄', '︾', '﹀', '︶', '︸', '〗', '〙', '〛',
}
_CJK_OPENERS = {
    '「', '『', '（', '【', '《', '"', "'", '‘', '“',
    '﹁', '﹃', '︽', '︿', '︵', '︷', '〖', '〘', '〚',
}
_ZERO_WIDTH_RE = re.compile(r'[\u200b\u200c\u200d\ufeff]')
_SPACE_RE = re.compile(r'\s+')
_DIALOGUE_TAG_RE = re.compile(
    r'^[\s"“”\'‘’\(\[\-—]*(?:'
    r'said|asked|replied|cried|murmured|whispered|answered|shouted|continued|'
    r'dijo|pregunt[oó]|respondi[oó]|murmur[oó]|contest[oó]|replic[oó]|'
    r'susurr[oó]|grit[oó]'
    r')\b',
    re.IGNORECASE,
)
_LOWERCASE_DIALOGUE_RE = re.compile(r'^[\s"“”\'‘’\(\[\-—]*[a-záéíóúñüç]', re.IGNORECASE)


class SentenceSplitter:
    """Sentence splitter with language-aware rules and light normalization."""

    def __init__(self, language: str = 'ja'):
        self.language = language
        self._splitter = None

    def _get_splitter(self):
        if self._splitter is None:
            import pysbd

            self._splitter = pysbd.Segmenter(
                language=self._map_language(self.language),
                clean=False,
            )
        return self._splitter

    @staticmethod
    def _map_language(lang: str) -> str:
        mapping = {
            'ja': 'ja',
            'jpn': 'ja',
            'zh': 'zh',
            'zho': 'zh',
            'en': 'en',
            'eng': 'en',
            'es': 'es',
            'spa': 'es',
            'fr': 'fr',
            'fra': 'fr',
            'de': 'de',
            'deu': 'de',
        }
        return mapping.get(lang, 'en')

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize extracted text before sentence splitting or audit."""

        if not text:
            return ''
        text = text.replace('\xa0', ' ').replace('\u3000', ' ')
        text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        text = _ZERO_WIDTH_RE.sub('', text)
        text = _SPACE_RE.sub(' ', text)
        return text.strip()

    def split(self, text: str) -> list[str]:
        """Split *text* into sentences and return non-empty normalized parts."""

        normalized = self.normalize_text(text)
        if not normalized:
            return []

        if self.language in ('ja', 'jpn', 'zh', 'zho'):
            sentences = self._split_cjk(normalized)
        else:
            sentences = self._merge_dialogue_segments(self._split_pysbd(normalized))

        cleaned = [self.normalize_text(sentence) for sentence in sentences]
        return [sentence for sentence in cleaned if sentence]

    def _split_pysbd(self, text: str) -> list[str]:
        splitter = self._get_splitter()
        return [segment for segment in splitter.segment(text) if segment.strip()]

    def _split_cjk(self, text: str) -> list[str]:
        """Split CJK text while keeping trailing quotes/brackets with the sentence."""

        sentences: list[str] = []
        start = 0
        idx = 0
        quote_depth = 0
        while idx < len(text):
            char = text[idx]
            if char in _CJK_OPENERS:
                quote_depth += 1
            elif char in _CJK_CLOSERS and quote_depth > 0:
                quote_depth -= 1
            if char not in _CJK_STOP_PUNCT:
                idx += 1
                continue

            end = idx + 1
            consumed_closers = 0
            while end < len(text) and text[end] in _CJK_CLOSERS:
                consumed_closers += 1
                end += 1
            if quote_depth > 0 and end == idx + 1:
                idx += 1
                continue
            candidate = text[start:end].strip()
            if candidate:
                sentences.append(candidate)
            if consumed_closers:
                quote_depth = max(quote_depth - consumed_closers, 0)
            start = end
            idx = end

        tail = text[start:].strip()
        if tail:
            if sentences:
                sentences[-1] = f'{sentences[-1]}{tail}'.strip()
            else:
                sentences.append(tail)
        return sentences

    def _merge_dialogue_segments(self, segments: list[str]) -> list[str]:
        if not segments:
            return []

        merged: list[str] = []
        for segment in segments:
            if (
                merged
                and (
                    self._should_merge_with_previous(merged[-1], segment)
                    or self._should_merge_colon_lead_in(merged[-1], segment)
                )
            ):
                merged[-1] = f'{merged[-1]} {segment}'.strip()
                continue
            merged.append(segment)
        return merged

    def _should_merge_with_previous(self, previous: str, current: str) -> bool:
        prev = previous.strip()
        curr = current.strip()
        if not prev or not curr:
            return False
        if prev.endswith(('"', '”', '’')) and (_DIALOGUE_TAG_RE.match(curr) or _LOWERCASE_DIALOGUE_RE.match(curr)):
            return True
        if curr in {'"', '”', '’', "''"}:
            return True
        return False

    def _should_merge_colon_lead_in(self, previous: str, current: str) -> bool:
        prev = previous.strip()
        curr = current.strip()
        if not prev or not curr:
            return False
        if prev.endswith(':') and curr[:1] in {'"', '“', '‘', '-', '—', '¿', '¡'}:
            return True
        return False
