"""XHTML 文本抽取：XHTML -> Segment 列表（含标签过滤与 CFI 定位）。

核心逻辑：遍历块级元素，收集可读文本片段，生成 range CFI，
可选按句子切分并为每个句子生成独立 CFI。
"""

from __future__ import annotations

from typing import Any

from ebooklib import epub
from lxml import etree

from bookalign.models.types import Segment
from bookalign.epub.cfi import (
    _local_tag,
    _readable_segments,
    _spine_index_of_item,
    _build_dom_path,
    _elem_children,
    generate_cfi_for_text_range,
    parse_item_xml,
)
from bookalign.epub.tag_filters import TagFilterConfig, should_skip_element
from bookalign.epub.sentence_splitter import SentenceSplitter


def extract_segments(
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    chapter_idx: int,
    config: TagFilterConfig | None = None,
    splitter: SentenceSplitter | None = None,
) -> list[Segment]:
    """Extract text segments from an XHTML document.

    Each block-level element (``<p>``, ``<div>``, etc.) becomes one or more
    ``Segment`` objects with precise range CFI positioning.

    Args:
        book: The parent EpubBook (needed for spine index in CFI).
        doc: The XHTML document (EpubHtml item).
        chapter_idx: Spine index of this chapter.
        config: Tag filtering configuration. Uses defaults if None.
        splitter: Optional sentence splitter. If provided, paragraphs are
            further split into sentence-level segments.

    Returns:
        List of Segment objects with CFI positioning.
    """
    if config is None:
        config = TagFilterConfig()

    root = parse_item_xml(doc)
    segments: list[Segment] = []
    paragraph_idx = 0

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue

        tag = _local_tag(elem.tag)
        if tag not in config.block_tags:
            continue

        if should_skip_element(elem, config):
            continue

        # Collect readable text from this block element
        readable_segs = _readable_segments_filtered(elem, config)
        full_text = ''.join(s['text'] for s in readable_segs)
        clean_text = full_text.strip()

        if not clean_text:
            continue

        # Compute text node range covering the full paragraph
        parent_segs = [s for s in readable_segs if s['type'] == 'parent']
        if not parent_segs:
            continue

        # Find first non-empty position
        first_tni, first_off = _find_text_start(readable_segs, full_text, clean_text)
        last_tni, last_off = _find_text_end(readable_segs, full_text, clean_text)

        if first_tni is None or last_tni is None:
            continue

        # Generate paragraph-level CFI
        para_cfi = generate_cfi_for_text_range(
            book, doc, elem, first_tni, first_off, last_tni, last_off,
            _root=root,
        )

        raw_html = etree.tostring(elem, encoding='unicode', method='html')

        if splitter is None:
            # Paragraph-level segment
            segments.append(Segment(
                text=clean_text,
                cfi=para_cfi or '',
                chapter_idx=chapter_idx,
                paragraph_idx=paragraph_idx,
                sentence_idx=None,
                raw_html=raw_html,
            ))
        else:
            # Sentence-level segments
            sentences = splitter.split(clean_text)
            sent_segments = _map_sentences_to_cfi(
                book, doc, elem, root,
                readable_segs, full_text, clean_text,
                sentences, chapter_idx, paragraph_idx,
                raw_html,
            )
            segments.extend(sent_segments)

        paragraph_idx += 1

    return segments


def _readable_segments_filtered(
    element, config: TagFilterConfig
) -> list[dict[str, Any]]:
    """Build readable text segments with filtering applied.

    Like ``cfi._readable_segments`` but uses the full TagFilterConfig
    to skip elements by tag name and CSS class.
    """
    skip_tags = config.skip_tags
    include_child_text_tags = frozenset({'ruby'})

    segs: list[dict[str, Any]] = []
    segs.append({'text': element.text or '', 'type': 'parent', 'tni': 0})

    for i, child in enumerate(element):
        tni = i + 1

        tag = _local_tag(child.tag)

        # Check if this child should contribute readable text
        if isinstance(tag, str) and tag in include_child_text_tags:
            ct = _child_readable_text_filtered(child, config)
            if ct:
                segs.append({'text': ct, 'type': 'child', 'after_tni': i})
        elif isinstance(tag, str) and not should_skip_element(child, config):
            # Inline elements (span, em, strong, a, etc.) that aren't skipped
            # contribute their readable text as child segments
            if tag not in config.block_tags:
                ct = _child_readable_text_filtered(child, config)
                if ct:
                    segs.append({'text': ct, 'type': 'child', 'after_tni': i})

        segs.append({'text': child.tail or '', 'type': 'parent', 'tni': tni})

    return segs


def _child_readable_text_filtered(element, config: TagFilterConfig) -> str:
    """Get readable text from a child element using TagFilterConfig."""
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in element:
        tag = _local_tag(child.tag)
        if isinstance(tag, str) and not should_skip_element(child, config):
            parts.append(_child_readable_text_filtered(child, config))
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts)


def _find_text_start(
    readable_segs: list[dict], full_text: str, clean_text: str
) -> tuple[int | None, int | None]:
    """Find the (tni, offset) of the first character of clean_text in readable segments."""
    # Find where clean_text starts in full_text
    start_pos = full_text.find(clean_text[0])
    if start_pos == -1:
        start_pos = 0
        # Skip leading whitespace
        for i, ch in enumerate(full_text):
            if not ch.isspace():
                start_pos = i
                break

    return _map_position_to_tni(readable_segs, start_pos)


def _find_text_end(
    readable_segs: list[dict], full_text: str, clean_text: str
) -> tuple[int | None, int | None]:
    """Find the (tni, offset) of the end of clean_text in readable segments."""
    # Find where clean_text ends in full_text
    idx = full_text.find(clean_text)
    if idx == -1:
        end_pos = len(full_text)
    else:
        end_pos = idx + len(clean_text)

    return _map_position_to_tni(readable_segs, end_pos)


def _map_position_to_tni(
    readable_segs: list[dict], pos: int
) -> tuple[int | None, int | None]:
    """Map a character position in concatenated readable text to (tni, offset)."""
    cum = 0
    for seg in readable_segs:
        seg_len = len(seg['text'])
        if seg['type'] == 'parent':
            if cum <= pos <= cum + seg_len:
                return (seg['tni'], pos - cum)
        cum += seg_len

    # Fallback: last parent segment
    for seg in reversed(readable_segs):
        if seg['type'] == 'parent':
            return (seg['tni'], len(seg['text']))
    return (None, None)


def _map_sentences_to_cfi(
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    element,
    root,
    readable_segs: list[dict[str, Any]],
    full_text: str,
    clean_text: str,
    sentences: list[str],
    chapter_idx: int,
    paragraph_idx: int,
    raw_html: str,
) -> list[Segment]:
    """Map split sentences back to CFI positions.

    For each sentence:
    1. Find its position in the clean text
    2. Map to readable segment positions
    3. Generate a range CFI
    """
    segments: list[Segment] = []

    # Build cumulative offsets for readable segments
    boundaries: list[tuple[int, int, dict]] = []
    cum = 0
    for seg in readable_segs:
        seg_len = len(seg['text'])
        boundaries.append((cum, cum + seg_len, seg))
        cum += seg_len

    # Offset of clean_text within full_text
    clean_start = full_text.find(clean_text)
    if clean_start == -1:
        clean_start = 0

    search_from = 0
    for sent_idx, sentence in enumerate(sentences):
        # Find sentence in clean_text
        sent_pos = clean_text.find(sentence, search_from)
        if sent_pos == -1:
            # Fallback: try stripped match
            sent_stripped = sentence.strip()
            sent_pos = clean_text.find(sent_stripped, search_from)
            if sent_pos == -1:
                continue
            sentence = sent_stripped

        sent_end = sent_pos + len(sentence)
        search_from = sent_end

        # Map to full_text positions
        abs_start = clean_start + sent_pos
        abs_end = clean_start + sent_end

        # Map to parent tni positions
        start_tni_off = _map_pos_to_parent(boundaries, abs_start, is_end=False)
        end_tni_off = _map_pos_to_parent(boundaries, abs_end, is_end=True)

        if start_tni_off is None or end_tni_off is None:
            segments.append(Segment(
                text=sentence,
                cfi='',
                chapter_idx=chapter_idx,
                paragraph_idx=paragraph_idx,
                sentence_idx=sent_idx,
                raw_html=raw_html,
            ))
            continue

        start_tni, start_off = start_tni_off
        end_tni, end_off = end_tni_off

        cfi = generate_cfi_for_text_range(
            book, doc, element,
            start_tni, start_off, end_tni, end_off,
            _root=root,
        )

        segments.append(Segment(
            text=sentence,
            cfi=cfi or '',
            chapter_idx=chapter_idx,
            paragraph_idx=paragraph_idx,
            sentence_idx=sent_idx,
            raw_html=raw_html,
        ))

    return segments


def _map_pos_to_parent(
    boundaries: list[tuple[int, int, dict]],
    pos: int,
    is_end: bool,
) -> tuple[int, int] | None:
    """Map a position in concatenated text to a parent text node (tni, offset).

    When the position falls inside a child segment, snap to nearest parent:
    - ``is_end=False``: snap backward to preceding parent's end
    - ``is_end=True``: snap forward to following parent's start
    """
    for i, (start, end, seg) in enumerate(boundaries):
        if not (start <= pos <= end):
            continue

        if start == end and pos == start:
            if seg['type'] == 'parent':
                return (seg['tni'], 0)
            continue

        if seg['type'] == 'parent':
            return (seg['tni'], pos - start)
        else:
            # Snap to nearest parent boundary
            if not is_end:
                for j in range(i - 1, -1, -1):
                    if boundaries[j][2]['type'] == 'parent':
                        s = boundaries[j][2]
                        return (s['tni'], len(s['text']))
            else:
                for j in range(i + 1, len(boundaries)):
                    if boundaries[j][2]['type'] == 'parent':
                        return (boundaries[j][2]['tni'], 0)
            return None

    return None
