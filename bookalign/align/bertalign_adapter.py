"""Bertalign-based text aligner adapter."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from bookalign.align.base import BaseAligner

_VENDOR_ROOT = Path(__file__).resolve().parents[1] / 'vendor' / 'bertalign'
_ISO_ALIASES = {
    'zh-cn': 'zh',
    'zh-tw': 'zh',
    'zh-hans': 'zh',
    'zh-hant': 'zh',
}


def _normalize_lang(lang: str | None) -> str | None:
    if not lang:
        return None
    return _ISO_ALIASES.get(lang.lower(), lang.lower())


def _ensure_vendor_path() -> None:
    vendor_path = str(_VENDOR_ROOT)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)


def _load_vendor_module():
    _ensure_vendor_path()
    return importlib.import_module('bertalign')


class BertalignAdapter(BaseAligner):
    """Project-facing adapter over the vendored Bertalign implementation."""

    def __init__(
        self,
        *,
        model_name: str = 'sentence-transformers/LaBSE',
        max_align: int = 5,
        top_k: int = 3,
        win: int = 5,
        skip: float = -0.1,
        margin: bool = True,
        len_penalty: bool = True,
        src_lang: str | None = None,
        tgt_lang: str | None = None,
        default_score: float = 1.0,
    ) -> None:
        self.model_name = model_name
        self.max_align = max_align
        self.top_k = top_k
        self.win = win
        self.skip = skip
        self.margin = margin
        self.len_penalty = len_penalty
        self.src_lang = _normalize_lang(src_lang)
        self.tgt_lang = _normalize_lang(tgt_lang)
        self.default_score = default_score

    def align(
        self,
        src_texts: list[str],
        tgt_texts: list[str],
    ) -> list[tuple[list[int], list[int], float]]:
        """Align already-split source/target texts and return bead indices."""
        if not src_texts or not tgt_texts:
            return []

        try:
            vendor = _load_vendor_module()
            vendor.configure_model(self.model_name)
            vendor_aligner = vendor.Bertalign(
                '\n'.join(src_texts),
                '\n'.join(tgt_texts),
                max_align=self.max_align,
                top_k=self.top_k,
                win=self.win,
                skip=self.skip,
                margin=self.margin,
                len_penalty=self.len_penalty,
                is_split=True,
                src_lang=self.src_lang,
                tgt_lang=self.tgt_lang,
            )
            vendor_aligner.align_sents()
        except ImportError as exc:
            raise RuntimeError(
                'Bertalign runtime dependencies are missing. Install the '
                'vendor requirements (for example: torch, faiss-cpu, numba, '
                'sentence-transformers, googletrans, sentence-splitter).'
            ) from exc

        return [
            (list(src_ids), list(tgt_ids), self.default_score)
            for src_ids, tgt_ids in vendor_aligner.result
        ]
