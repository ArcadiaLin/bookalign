"""多语言句子切分统一接口。"""

import re


class SentenceSplitter:
    """Sentence splitter with language-aware rules.

    Uses pysbd as the primary backend, with special handling for
    CJK languages (Japanese, Chinese).
    """

    def __init__(self, language: str = 'ja'):
        self.language = language
        self._splitter = None

    def _get_splitter(self):
        if self._splitter is None:
            import pysbd
            lang = self._map_language(self.language)
            self._splitter = pysbd.Segmenter(language=lang, clean=False)
        return self._splitter

    @staticmethod
    def _map_language(lang: str) -> str:
        """Map language codes to pysbd-supported codes."""
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

    def split(self, text: str) -> list[str]:
        """Split *text* into sentences.

        Returns a list of non-empty sentence strings.
        Empty/whitespace-only segments are filtered out.
        """
        if not text or not text.strip():
            return []

        if self.language in ('ja', 'jpn', 'zh', 'zho'):
            return self._split_cjk(text)

        return self._split_pysbd(text)

    def _split_pysbd(self, text: str) -> list[str]:
        """Split using pysbd."""
        splitter = self._get_splitter()
        sentences = splitter.segment(text)
        return [s for s in sentences if s.strip()]

    def _split_cjk(self, text: str) -> list[str]:
        """Split CJK text on sentence-ending punctuation.

        Handles: 。！？ followed by optional closing quotes/brackets.
        Falls back to pysbd for text without CJK punctuation.
        """
        # Pattern: sentence-ending punctuation + optional closing quotes
        pattern = re.compile(
            r'([。！？!?]'
            r'[」』）\)】》〉"\']*'
            r')'
        )

        parts = pattern.split(text)
        if len(parts) <= 1:
            # No CJK sentence-ending punctuation found, use pysbd
            return self._split_pysbd(text)

        # Reassemble: text + delimiter pairs
        sentences: list[str] = []
        current = ''
        for i, part in enumerate(parts):
            current += part
            # Odd indices are the delimiters (captured group)
            if i % 2 == 1:
                stripped = current.strip()
                if stripped:
                    sentences.append(stripped)
                current = ''

        # Handle trailing text after last delimiter
        if current.strip():
            if sentences:
                sentences[-1] += current.rstrip()
            else:
                sentences.append(current.strip())

        return [s for s in sentences if s.strip()]
