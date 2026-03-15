"""Core data structures for extraction and alignment."""

from dataclasses import dataclass, field


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
class Segment:
    """A paragraph-level or sentence-level text unit used for alignment."""

    text: str
    cfi: str
    chapter_idx: int
    paragraph_idx: int
    sentence_idx: int | None
    raw_html: str = ''
    element_xpath: str = ''
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
