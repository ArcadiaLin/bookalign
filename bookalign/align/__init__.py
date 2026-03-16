"""Alignment APIs."""

from bookalign.align.aligner import (
    align_segments,
    align_segments_with_bertalign,
    build_aligned_pairs,
)
from bookalign.align.bertalign_adapter import BertalignAdapter

__all__ = [
    'BertalignAdapter',
    'align_segments',
    'align_segments_with_bertalign',
    'build_aligned_pairs',
]
