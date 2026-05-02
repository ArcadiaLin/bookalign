"""Core data structures for extraction and alignment."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SpineItem:
    """Wrapper for an item in the book spine."""

    index: int
    item: object


@dataclass
class TextSpan:
    """A readable text fragment and its source position in the XHTML tree."""

    text: str
    xpath: str
    text_node_index: int
    char_offset: int
    source_kind: str = 'text'
    cfi_text_node_index: int | None = None
    cfi_exact: bool = False


@dataclass
class DebugSpan:
    """Debug-only span metadata for inspection and reports."""

    xpath: str
    tag: str
    text_preview: str
    action: str = ''
    policy_name: str = ''


@dataclass
class JumpFragment:
    """Structured note/jump metadata extracted from inline markup."""

    kind: str
    text: str = ''
    start: int | None = None
    end: int | None = None
    href: str = ''
    anchor_id: str = ''


@dataclass
class Segment:
    """A paragraph-level or sentence-level text unit used for alignment."""

    text: str
    cfi: str
    chapter_idx: int
    paragraph_idx: int
    sentence_idx: int | None
    paragraph_cfi: str = ''
    text_start: int | None = None
    text_end: int | None = None
    raw_html: str = ''
    element_xpath: str = ''
    has_jump_markup: bool = False
    is_note_like: bool = False
    alignment_role: str = 'align'
    paratext_kind: str = 'body'
    filter_reason: str = ''
    jump_fragments: list[JumpFragment] = field(default_factory=list)
    spans: list[TextSpan] = field(default_factory=list)


@dataclass
class AlignedPair:
    """A group of aligned segments."""

    source: list[Segment]
    target: list[Segment]
    score: float


@dataclass
class AlignmentResult:
    """Alignment result for a whole book."""

    pairs: list[AlignedPair]
    source_lang: str
    target_lang: str
    granularity: str
    extract_mode: str = 'filtered_preserve'
    retained_source_segments: list[Segment] = field(default_factory=list)
    retained_target_segments: list[Segment] = field(default_factory=list)


@dataclass
class ChapterInfo:
    """Inferred chapter metadata for a single EPUB spine document."""

    chapter_id: str
    chapter_idx: int
    spine_idx: int
    title: str
    label: str
    is_paratext: bool = False
    sentence_count: int = 0
    paragraph_count: int = 0
    alignment_sentence_count: int = 0
    alignment_paragraph_count: int = 0


@dataclass
class SegmentRecord:
    """Segment plus stable chapter metadata for engineering APIs."""

    segment: Segment
    chapter_id: str
    chapter_title: str
    granularity: str


@dataclass
class BookExtraction:
    """Serializable extraction result for one EPUB."""

    language: str
    extract_mode: str
    default_granularity: str
    chapters: list[ChapterInfo] = field(default_factory=list)
    sentence_segments: list[SegmentRecord] = field(default_factory=list)
    paragraph_segments: list[SegmentRecord] = field(default_factory=list)
    source_path: str = ''

    @property
    def path(self) -> Path | None:
        if not self.source_path:
            return None
        return Path(self.source_path)
