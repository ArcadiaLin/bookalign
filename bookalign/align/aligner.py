"""Alignment orchestration helpers."""

from __future__ import annotations

from bookalign.align.base import BaseAligner
from bookalign.align.bertalign_adapter import BertalignAdapter
from bookalign.models.types import AlignedPair, AlignmentResult, Segment


def build_aligned_pairs(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    beads: list[tuple[list[int], list[int], float]],
) -> list[AlignedPair]:
    """Map alignment beads back to segment groups."""
    pairs: list[AlignedPair] = []
    for src_ids, tgt_ids, score in beads:
        source = [src_segments[idx] for idx in src_ids]
        target = [tgt_segments[idx] for idx in tgt_ids]
        pairs.append(AlignedPair(source=source, target=target, score=score))
    return pairs


def align_segments(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    *,
    source_lang: str,
    target_lang: str,
    granularity: str,
    aligner: BaseAligner | None = None,
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


def align_segments_with_bertalign(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    *,
    source_lang: str,
    target_lang: str,
    granularity: str,
    **kwargs,
) -> AlignmentResult:
    """Convenience entry point for the current default aligner."""
    return align_segments(
        src_segments,
        tgt_segments,
        source_lang=source_lang,
        target_lang=target_lang,
        granularity=granularity,
        aligner=BertalignAdapter(
            src_lang=source_lang,
            tgt_lang=target_lang,
            **kwargs,
        ),
    )
