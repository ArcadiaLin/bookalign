"""Alignment orchestration helpers."""

from __future__ import annotations

from align.bertalign_adapter import BertalignAdapter
from models.types import AlignedPair, AlignmentResult, Segment


def build_aligned_pairs(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    beads: list[tuple[list[int], list[int], float]],
) -> list[AlignedPair]:
    """Map alignment beads back to segment groups."""
    pairs: list[AlignedPair] = []
    covered_src: set[int] = set()
    covered_tgt: set[int] = set()
    for src_ids, tgt_ids, score in beads:
        covered_src.update(src_ids)
        covered_tgt.update(tgt_ids)
        source = [src_segments[idx] for idx in src_ids]
        target = [tgt_segments[idx] for idx in tgt_ids]
        pairs.append(AlignedPair(source=source, target=target, score=score))

    for idx, segment in enumerate(src_segments):
        if idx not in covered_src:
            pairs.append(AlignedPair(source=[segment], target=[], score=0.0))
    for idx, segment in enumerate(tgt_segments):
        if idx not in covered_tgt:
            pairs.append(AlignedPair(source=[], target=[segment], score=0.0))

    def _pair_order_key(pair: AlignedPair) -> tuple[int, int]:
        if pair.source:
            return (pair.source[0].chapter_idx, pair.source[0].paragraph_idx)
        if pair.target:
            return (pair.target[0].chapter_idx, pair.target[0].paragraph_idx)
        return (10**9, 10**9)

    pairs.sort(key=_pair_order_key)
    return pairs


def align_segments(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    *,
    source_lang: str,
    target_lang: str,
    granularity: str,
    aligner: BertalignAdapter | None = None,
) -> AlignmentResult:
    """Align project segments and return the project-level result model."""
    engine = aligner or BertalignAdapter(
        src_lang=source_lang,
        tgt_lang=target_lang,
    )
    beads = engine.align(
        [segment.text for segment in src_segments],
        [segment.text for segment in tgt_segments],
    )
    return AlignmentResult(
        pairs=build_aligned_pairs(src_segments, tgt_segments, beads),
        source_lang=source_lang,
        target_lang=target_lang,
        granularity=granularity,
    )
