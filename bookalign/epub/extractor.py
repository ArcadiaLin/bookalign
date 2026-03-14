"""XHTML text extraction with tag filtering, trace spans, and CFI mapping."""

from __future__ import annotations

from typing import Iterable
import re

from ebooklib import epub
from lxml import etree

from bookalign.epub.cfi import generate_cfi_for_text_range, parse_item_xml, resolve_cfi
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.epub.tag_filters import (
    TagFilterConfig,
    _local_tag,
    is_block_element,
    is_structural_container,
    should_skip_element,
)
from bookalign.models.types import Segment, TextSpan


def extract_segments(
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    chapter_idx: int,
    config: TagFilterConfig | None = None,
    splitter: SentenceSplitter | None = None,
) -> list[Segment]:
    """Extract paragraph or sentence segments from an XHTML document."""

    config = config or TagFilterConfig()
    root = parse_item_xml(doc)
    tree = root.getroottree()
    segments: list[Segment] = []
    paragraph_idx = 0

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        if not is_block_element(elem, config):
            continue
        if should_skip_element(elem, config) or is_structural_container(elem, config):
            continue

        spans = _collect_text_spans(elem, tree, config)
        if not spans:
            continue

        full_text = ''.join(span.text for span in spans)
        clean_text = full_text.strip()
        if not clean_text:
            continue

        trimmed_spans, start_tni, start_off, end_tni, end_off = _trim_spans(spans)
        if not trimmed_spans:
            continue

        para_cfi = generate_cfi_for_text_range(
            book,
            doc,
            elem,
            start_tni,
            start_off,
            end_tni,
            end_off,
            _root=root,
        )
        raw_html = etree.tostring(elem, encoding='unicode', method='html')
        element_xpath = tree.getpath(elem)

        if splitter is None:
            segments.append(
                Segment(
                    text=''.join(span.text for span in trimmed_spans),
                    cfi=para_cfi or '',
                    chapter_idx=chapter_idx,
                    paragraph_idx=paragraph_idx,
                    sentence_idx=None,
                    raw_html=raw_html,
                    element_xpath=element_xpath,
                    spans=trimmed_spans,
                )
            )
        else:
            sentences = splitter.split(''.join(span.text for span in trimmed_spans))
            if not sentences:
                sentences = [''.join(span.text for span in trimmed_spans)]
            segments.extend(
                _map_sentences_to_segments(
                    book=book,
                    doc=doc,
                    element=elem,
                    root=root,
                    chapter_idx=chapter_idx,
                    paragraph_idx=paragraph_idx,
                    raw_html=raw_html,
                    element_xpath=element_xpath,
                    spans=trimmed_spans,
                    sentences=sentences,
                )
            )

        paragraph_idx += 1

    return segments


def extract_text_from_cfi(
    book: epub.EpubBook,
    cfi: str,
    config: TagFilterConfig | None = None,
) -> str:
    """Resolve a segment CFI and recover cleaned readable text."""

    config = config or TagFilterConfig()
    resolved = resolve_cfi(cfi, book)
    if not resolved or resolved.get('type') != 'range':
        return ''

    start = resolved['start'].get('target')
    end = resolved['end'].get('target')
    if not start or not end:
        return ''
    if start.get('type') != 'text' or end.get('type') != 'text':
        return ''
    if start.get('node') is not end.get('node'):
        return ''

    node = start['node']
    root = resolved['start'].get('root')
    if root is None:
        return ''

    spans = _collect_text_spans(node, root.getroottree(), config)
    if not spans:
        return ''

    return _extract_text_from_spans(
        spans,
        start['text_node_index'],
        start['offset'],
        end['text_node_index'],
        end['offset'],
    ).strip()


def _normalize_fragment(text: str) -> str:
    """Normalize a single XHTML text fragment without losing word boundaries."""

    if not text:
        return ''
    text = (
        text.replace('\xa0', ' ')
        .replace('\u3000', ' ')
        .replace('\u200b', '')
        .replace('\u200c', '')
        .replace('\u200d', '')
        .replace('\ufeff', '')
        .replace('\xad', '')
    )
    text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    return re.sub(r'\s+', ' ', text)


def _append_span(spans: list[TextSpan], span: TextSpan) -> None:
    """Append a span while smoothing duplicated whitespace at boundaries."""

    text = _normalize_fragment(span.text)
    if not text:
        return

    if spans:
        prev = spans[-1]
        if prev.text.endswith(' ') and text.startswith(' '):
            text = text.lstrip()
    if not text:
        return

    span.text = text
    spans.append(span)


def _direct_text_node_index(element, child=None) -> int:
    """Return the direct text node index within *element*."""

    if child is None:
        return 0
    element_children = [node for node in element if isinstance(node.tag, str)]
    return element_children.index(child) + 1


def _iter_readable_text_parts(
    element,
    tree,
    config: TagFilterConfig,
) -> Iterable[TextSpan]:
    """Yield readable text spans in DOM order for a paragraph element."""

    def walk(node, anchor_tni: int):
        if should_skip_element(node, config):
            return

        if node.text:
            yield TextSpan(
                text=node.text,
                xpath=tree.getpath(node),
                text_node_index=0,
                char_offset=0,
                source_kind='text',
                cfi_text_node_index=anchor_tni if node is not element else 0,
                cfi_exact=node is element,
            )

        for child_idx, child in enumerate(node):
            if not isinstance(child.tag, str):
                if child.tail:
                    yield TextSpan(
                        text=child.tail,
                        xpath=tree.getpath(node),
                        text_node_index=child_idx + 1,
                        char_offset=0,
                        source_kind='tail',
                        cfi_text_node_index=anchor_tni,
                        cfi_exact=False,
                    )
                continue

            child_anchor = child_idx if node is element else anchor_tni
            if should_skip_element(child, config):
                if child.tail:
                    yield TextSpan(
                        text=child.tail,
                        xpath=tree.getpath(node),
                        text_node_index=child_idx + 1,
                        char_offset=0,
                        source_kind='tail',
                        cfi_text_node_index=_direct_text_node_index(node, child) if node is element else anchor_tni,
                        cfi_exact=node is element,
                    )
                continue

            if is_block_element(child, config):
                continue

            yield from walk(child, child_anchor if node is element else anchor_tni)

            if child.tail:
                yield TextSpan(
                    text=child.tail,
                    xpath=tree.getpath(node),
                    text_node_index=_direct_text_node_index(node, child),
                    char_offset=0,
                    source_kind='tail',
                    cfi_text_node_index=_direct_text_node_index(node, child) if node is element else anchor_tni,
                    cfi_exact=node is element,
                )

    yield from walk(element, 0)


def _collect_text_spans(element, tree, config: TagFilterConfig) -> list[TextSpan]:
    """Collect normalized readable text spans for *element*."""

    spans: list[TextSpan] = []
    for span in _iter_readable_text_parts(element, tree, config):
        _append_span(spans, span)
    return spans


def _trim_spans(
    spans: list[TextSpan],
) -> tuple[list[TextSpan], int, int, int, int]:
    """Trim leading and trailing whitespace while keeping source trace intact."""

    if not spans:
        return [], 0, 0, 0, 0

    trimmed = [TextSpan(**span.__dict__) for span in spans]
    parent_lengths = _parent_text_lengths(trimmed)

    first_idx = 0
    while first_idx < len(trimmed) and not trimmed[first_idx].text.strip():
        first_idx += 1
    if first_idx == len(trimmed):
        return [], 0, 0, 0, 0

    last_idx = len(trimmed) - 1
    while last_idx >= 0 and not trimmed[last_idx].text.strip():
        last_idx -= 1

    trimmed = trimmed[first_idx:last_idx + 1]

    leading = len(trimmed[0].text) - len(trimmed[0].text.lstrip())
    trailing = len(trimmed[-1].text) - len(trimmed[-1].text.rstrip())
    if leading:
        trimmed[0].char_offset += leading
        trimmed[0].text = trimmed[0].text[leading:]
    if trailing:
        trimmed[-1].text = trimmed[-1].text[:-trailing]

    start_tni, start_off = _span_start_for_cfi(trimmed[0], parent_lengths)
    end_tni, end_off = _span_end_for_cfi(trimmed[-1], parent_lengths)
    return trimmed, start_tni, start_off, end_tni, end_off


def _parent_text_lengths(spans: list[TextSpan]) -> dict[int, int]:
    """Return normalized lengths of the paragraph's direct text nodes."""

    lengths: dict[int, int] = {}
    for span in spans:
        if span.cfi_exact and span.cfi_text_node_index is not None:
            lengths[span.cfi_text_node_index] = len(span.text)
    return lengths


def _span_start_for_cfi(
    span: TextSpan,
    parent_lengths: dict[int, int],
) -> tuple[int, int]:
    """Map a span start to paragraph-relative CFI coordinates."""

    if span.cfi_text_node_index is None:
        return 0, 0
    if span.cfi_exact:
        return span.cfi_text_node_index, span.char_offset
    return span.cfi_text_node_index, parent_lengths.get(span.cfi_text_node_index, 0)


def _span_end_for_cfi(
    span: TextSpan,
    parent_lengths: dict[int, int],
) -> tuple[int, int]:
    """Map a span end to paragraph-relative CFI coordinates."""

    if span.cfi_text_node_index is None:
        return 0, 0
    if span.cfi_exact:
        return span.cfi_text_node_index, span.char_offset + len(span.text)
    return span.cfi_text_node_index + 1, 0


def _map_sentences_to_segments(
    *,
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    element,
    root,
    chapter_idx: int,
    paragraph_idx: int,
    raw_html: str,
    element_xpath: str,
    spans: list[TextSpan],
    sentences: list[str],
) -> list[Segment]:
    """Map split sentences back to subsets of paragraph spans."""

    segments: list[Segment] = []
    if not spans:
        return segments

    if len(sentences) == 1:
        start_tni, start_off = _span_start_for_cfi(spans[0], _parent_text_lengths(spans))
        end_tni, end_off = _span_end_for_cfi(spans[-1], _parent_text_lengths(spans))
        cfi = generate_cfi_for_text_range(
            book,
            doc,
            element,
            start_tni,
            start_off,
            end_tni,
            end_off,
            _root=root,
        )
        return [
            Segment(
                text=''.join(span.text for span in spans),
                cfi=cfi or '',
                chapter_idx=chapter_idx,
                paragraph_idx=paragraph_idx,
                sentence_idx=0,
                raw_html=raw_html,
                element_xpath=element_xpath,
                spans=[TextSpan(**span.__dict__) for span in spans],
            )
        ]

    full_text = ''.join(span.text for span in spans)
    boundaries: list[tuple[int, int, TextSpan]] = []
    cursor = 0
    for span in spans:
        start = cursor
        cursor += len(span.text)
        boundaries.append((start, cursor, span))
    parent_lengths = _parent_text_lengths(spans)

    search_from = 0
    for sentence_idx, sentence in enumerate(sentences):
        if not sentence:
            continue

        sent_start = full_text.find(sentence, search_from)
        if sent_start < 0:
            sentence = sentence.strip()
            sent_start = full_text.find(sentence, search_from)
            if sent_start < 0:
                normalized_sentence = SentenceSplitter.normalize_text(sentence)
                normalized_full = SentenceSplitter.normalize_text(full_text)
                continue
        sent_end = sent_start + len(sentence)
        search_from = sent_end

        sentence_spans = _slice_spans(boundaries, sent_start, sent_end)
        if not sentence_spans:
            continue

        start_span = sentence_spans[0]
        end_span = sentence_spans[-1]
        start_tni, start_off = _span_start_for_cfi(start_span, parent_lengths)
        end_tni, end_off = _span_end_for_cfi(end_span, parent_lengths)
        cfi = generate_cfi_for_text_range(
            book,
            doc,
            element,
            start_tni,
            start_off,
            end_tni,
            end_off,
            _root=root,
        )
        segments.append(
            Segment(
                text=''.join(span.text for span in sentence_spans),
                cfi=cfi or '',
                chapter_idx=chapter_idx,
                paragraph_idx=paragraph_idx,
                sentence_idx=sentence_idx,
                raw_html=raw_html,
                element_xpath=element_xpath,
                spans=sentence_spans,
            )
        )

    return segments


def _slice_spans(
    boundaries: list[tuple[int, int, TextSpan]],
    sent_start: int,
    sent_end: int,
) -> list[TextSpan]:
    """Return the subset of spans covered by a sentence range."""

    sliced: list[TextSpan] = []
    for start, end, span in boundaries:
        overlap_start = max(start, sent_start)
        overlap_end = min(end, sent_end)
        if overlap_start >= overlap_end:
            continue
        relative_start = overlap_start - start
        relative_end = overlap_end - start
        sliced.append(
            TextSpan(
                text=span.text[relative_start:relative_end],
                xpath=span.xpath,
                text_node_index=span.text_node_index,
                char_offset=span.char_offset + relative_start,
                source_kind=span.source_kind,
                cfi_text_node_index=span.cfi_text_node_index,
                cfi_exact=span.cfi_exact,
            )
        )
    return sliced


def _extract_text_from_spans(
    spans: list[TextSpan],
    start_tni: int,
    start_off: int,
    end_tni: int,
    end_off: int,
) -> str:
    """Recover cleaned text between paragraph-relative CFI boundaries."""

    parts: list[str] = []
    for span in spans:
        if span.cfi_text_node_index is None:
            continue

        if span.cfi_exact:
            tni = span.cfi_text_node_index
            if tni < start_tni or tni > end_tni:
                continue
            span_start = span.char_offset
            span_end = span.char_offset + len(span.text)
            left = span_start
            right = span_end
            if tni == start_tni:
                left = max(left, start_off)
            if tni == end_tni:
                right = min(right, end_off)
            if left >= right:
                continue
            rel_left = left - span.char_offset
            rel_right = right - span.char_offset
            parts.append(span.text[rel_left:rel_right])
            continue

        anchor = span.cfi_text_node_index
        if start_tni <= anchor < end_tni:
            parts.append(span.text)

    return ''.join(parts)
