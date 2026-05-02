"""Policy-driven XHTML extraction with trace spans and CFI mapping."""

from __future__ import annotations

from collections.abc import Iterable
import re

from ebooklib import epub
from lxml import etree

from epub.cfi import generate_cfi_for_text_range, parse_item_xml, resolve_cfi
from epub.sentence_splitter import SentenceSplitter
from epub.tag_filters import (
    ExtractAction,
    TagFilterConfig,
    _local_tag,
    build_tag_filter_config,
    get_extract_action,
    is_block_element,
    is_structural_container,
    match_element_policy,
)
from models.types import DebugSpan, JumpFragment, Segment, TextSpan

_SENTENCE_PUNCT_RE = re.compile(r'[。！？!?…]|[.!?]["”’」』）)]?$')
_LATIN_LETTER_RE = re.compile(r'[A-Za-z]')
_LOWERCASE_START_RE = re.compile(r'^[\s"“”\'‘’\(\[\-—]*[a-záéíóúñüç]')
_DIALOGUE_TAG_RE = re.compile(
    r'^[\s"“”\'‘’\(\[\-—]*(?:'
    r'said|asked|replied|cried|murmured|whispered|answered|shouted|continued|'
    r'dijo|pregunt[oó]|respondi[oó]|murmur[oó]|contest[oó]|replic[oó]|'
    r'susurr[oó]|grit[oó]'
    r')\b',
    re.IGNORECASE,
)
_NOTE_ID_RE = re.compile(
    r'(?:^|[-_])(?:fnref|noteref|footnote-ref|footnote|endnote|note|fn|backlink|backref|注)(?:[-_0-9].*)?$',
    re.IGNORECASE,
)
_NOTE_HREF_RE = re.compile(r'#(?:fn|note|footnote|endnote|注)', re.IGNORECASE)


def extract_segments(
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    chapter_idx: int,
    config: TagFilterConfig | None = None,
    splitter: SentenceSplitter | None = None,
    extract_mode: str = 'filtered_preserve',
) -> list[Segment]:
    """Extract paragraph or sentence segments from an XHTML document."""

    if config is None:
        config = build_tag_filter_config(extract_mode)
    root = parse_item_xml(doc)
    tree = root.getroottree()
    segments: list[Segment] = []
    paragraph_idx = 0

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        if _has_skipped_ancestor(elem, config):
            continue
        if get_extract_action(elem, config) != ExtractAction.BLOCK_BREAK:
            continue
        if is_structural_container(elem, config):
            continue

        spans = _collect_text_spans(elem, tree, config)
        if not spans:
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
        paragraph_text = ''.join(span.text for span in trimmed_spans)
        should_emit, alignment_role, paratext_kind, filter_reason = _segment_extraction_decision(
            elem,
            paragraph_text,
            raw_html,
            config,
            extract_mode=extract_mode,
        )
        if not should_emit:
            continue

        paragraph_jumps = _collect_jump_fragments(
            element=elem,
            spans=trimmed_spans,
            boundaries=_build_span_boundaries(trimmed_spans),
        )
        has_jump_markup = bool(paragraph_jumps)
        is_note_like = _is_note_like_block(elem)

        if splitter is None:
            segments.append(
                Segment(
                    text=paragraph_text,
                    cfi=para_cfi or '',
                    chapter_idx=chapter_idx,
                    paragraph_idx=paragraph_idx,
                    sentence_idx=None,
                    paragraph_cfi=para_cfi or '',
                    text_start=0,
                    text_end=len(paragraph_text),
                    raw_html=raw_html,
                    element_xpath=element_xpath,
                    has_jump_markup=has_jump_markup,
                    is_note_like=is_note_like,
                    alignment_role=alignment_role,
                    paratext_kind=paratext_kind,
                    filter_reason=filter_reason,
                    jump_fragments=paragraph_jumps,
                    spans=[_clone_span(span) for span in trimmed_spans],
                )
            )
        else:
            sentences = _split_paragraph_sentences(trimmed_spans, paragraph_text, splitter)
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
                    paragraph_cfi=para_cfi or '',
                    spans=trimmed_spans,
                    sentences=sentences,
                    paragraph_jump_fragments=paragraph_jumps,
                    is_note_like=is_note_like,
                    alignment_role=alignment_role,
                    paratext_kind=paratext_kind,
                    filter_reason=filter_reason,
                )
            )

        paragraph_idx += 1

    return segments


def _should_emit_segment(element, text: str, raw_html: str, config: TagFilterConfig) -> bool:
    should_emit, _, _, _ = _segment_extraction_decision(
        element,
        text,
        raw_html,
        config,
        extract_mode='filtered_preserve',
    )
    return should_emit


def _segment_extraction_decision(
    element,
    text: str,
    raw_html: str,
    config: TagFilterConfig,
    *,
    extract_mode: str,
) -> tuple[bool, str, str, str]:
    normalized = SentenceSplitter.normalize_text(text)
    if not normalized:
        return False, 'retain', 'metadata', 'empty'

    if extract_mode != 'filtered_preserve':
        raise ValueError(f'Unsupported extract_mode: {extract_mode}')

    paratext_kind, filter_reason = _classify_paratext_kind(element, normalized, config)
    if paratext_kind == 'body':
        return True, 'align', 'body', ''
    return True, 'retain', paratext_kind, filter_reason


def _classify_paratext_kind(element, text: str, config: TagFilterConfig) -> tuple[str, str]:
    classes = set(element.get('class', '').split())
    element_id = element.get('id', '')

    if _element_has_note_traits(element):
        return 'note_body', 'note_block'

    if classes & {'toc', 'contents'}:
        return 'toc', 'toc_class'
    if re.search(r'(toc|contents|nav)', element_id, re.IGNORECASE):
        return 'toc', 'toc_id'
    if _looks_like_navigation_block(element, text):
        return 'toc', 'navigation_block'

    if classes & {'title', 'titlepage'}:
        return 'frontmatter', 'title_class'
    if classes & {'copyright', 'license'}:
        return 'metadata', 'copyright_class'
    if re.search(r'(copyright|license|colophon|isbn)', element_id, re.IGNORECASE):
        return 'metadata', 'metadata_id'

    if not config.apply_segment_heuristics:
        return 'body', ''

    lower = text.casefold()
    if any(re.search(pattern, lower, re.IGNORECASE) for pattern in config.skip_text_patterns):
        return 'metadata', 'skip_text_pattern'
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in config.skip_line_patterns):
        return 'metadata', 'skip_line_pattern'

    words = text.split()
    if len(words) <= 12 and any(re.search(pattern, text, re.IGNORECASE) for pattern in config.skip_heading_patterns):
        return 'chapter_heading', 'skip_heading_pattern'
    if len(words) <= 10 and not _SENTENCE_PUNCT_RE.search(text) and _looks_like_heading_or_metadata(text):
        return 'chapter_heading', 'heading_or_metadata'

    return 'body', ''


def _looks_like_heading_or_metadata(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if re.fullmatch(r'[\W_]+', stripped):
        return True
    if re.fullmatch(r'[0-9]{1,4}(?:/[0-9]{1,4}){0,2}', stripped):
        return True
    if re.fullmatch(r'[A-Z][A-Za-z.\- ]{2,}', stripped) and stripped == stripped.upper():
        return True
    if _LATIN_LETTER_RE.search(stripped) and stripped == stripped.title() and len(stripped.split()) <= 8:
        return True
    if _looks_like_author_line(stripped):
        return True
    if re.fullmatch(r'[一二三四五六七八九十百千〇零0-9 ]+[章节回部篇卷]', stripped):
        return True
    return False


def _looks_like_author_line(text: str) -> bool:
    words = text.split()
    if not (2 <= len(words) <= 6):
        return False
    allowed_lower = {'de', 'del', 'la', 'las', 'los', 'of', 'the', 'y'}
    capitals = 0
    for word in words:
        if word.casefold() in allowed_lower:
            continue
        if word[:1].isupper():
            capitals += 1
    return capitals >= max(2, len(words) - 1)


def _looks_like_navigation_block(element, text: str) -> bool:
    anchors = [child for child in element.iterdescendants() if isinstance(child.tag, str) and _local_tag(child.tag) == 'a']
    if not anchors:
        return False
    hrefs = [href for anchor in anchors if (href := anchor.get('href', '').strip())]
    if len(hrefs) >= 3 and ('|' in text or all('#' in href for href in hrefs)):
        return True
    if _local_tag(element.tag) == 'li' and hrefs and all('#' in href for href in hrefs):
        return True
    return False


def _has_skipped_ancestor(element, config: TagFilterConfig) -> bool:
    parent = element.getparent()
    while parent is not None and isinstance(getattr(parent, 'tag', None), str):
        if get_extract_action(parent, config) == ExtractAction.SKIP_ENTIRE:
            return True
        parent = parent.getparent()
    return False


def _is_note_href(href: str) -> bool:
    normalized = (href or '').strip()
    return bool(normalized and _NOTE_HREF_RE.search(normalized))


def _is_note_id(anchor_id: str) -> bool:
    normalized = (anchor_id or '').strip()
    return bool(normalized and _NOTE_ID_RE.search(normalized))


def _element_has_note_traits(element) -> bool:
    if not isinstance(getattr(element, 'tag', None), str):
        return False
    classes = set((element.get('class') or '').split())
    epub_types = set((element.get('{http://www.idpf.org/2007/ops}type') or '').split())
    if classes & {'noteref', 'footnote-ref', 'super', 'annotation'}:
        return True
    if epub_types & {'noteref', 'footnote', 'endnote'}:
        return True
    if _is_note_id(element.get('id', '')):
        return True
    return _is_note_href(element.get('href', ''))


def _is_note_like_block(element) -> bool:
    if _element_has_note_traits(element):
        return True
    return any(_element_has_note_traits(child) for child in element.iterdescendants() if isinstance(child.tag, str))


def _nearest_jump_element(node):
    current = node
    while current is not None and isinstance(getattr(current, 'tag', None), str):
        if _local_tag(current.tag) == 'a' and _is_note_href(current.get('href', '')):
            return current
        current = current.getparent()
    return None


def _collect_jump_fragments(
    *,
    element,
    spans: list[TextSpan],
    boundaries: list[tuple[int, int, TextSpan]],
) -> list[JumpFragment]:
    fragments: list[JumpFragment] = []
    active_href: str | None = None
    active_start: int | None = None
    active_end: int | None = None
    active_text_parts: list[str] = []

    def flush_href() -> None:
        nonlocal active_href, active_start, active_end, active_text_parts
        if active_href and active_start is not None and active_end is not None and active_start < active_end:
            fragments.append(
                JumpFragment(
                    kind='href',
                    text=''.join(active_text_parts),
                    start=active_start,
                    end=active_end,
                    href=active_href,
                )
            )
        active_href = None
        active_start = None
        active_end = None
        active_text_parts = []

    for start, end, span in boundaries:
        owner = getattr(span, '_node', None)
        jump_node = _nearest_jump_element(owner) if owner is not None else None
        href = (jump_node.get('href') or '').strip() if jump_node is not None else ''
        if not href:
            flush_href()
            continue
        if href != active_href:
            flush_href()
            active_href = href
            active_start = start
        active_end = end
        active_text_parts.append(span.text)
    flush_href()

    seen_ids: set[str] = set()
    for node in [element, *[child for child in element.iterdescendants() if isinstance(child.tag, str)]]:
        anchor_id = (node.get('id') or '').strip()
        if anchor_id and _is_note_id(anchor_id) and anchor_id not in seen_ids:
            fragments.append(
                JumpFragment(
                    kind='id',
                    anchor_id=anchor_id,
                )
            )
            seen_ids.add(anchor_id)

    return fragments


def _slice_jump_fragments(
    fragments: list[JumpFragment],
    sent_start: int,
    sent_end: int,
) -> list[JumpFragment]:
    sliced: list[JumpFragment] = []
    for fragment in fragments:
        if fragment.kind == 'id':
            if sent_start == 0:
                sliced.append(fragment)
            continue
        if fragment.start is None or fragment.end is None:
            continue
        overlap_start = max(sent_start, fragment.start)
        overlap_end = min(sent_end, fragment.end)
        if overlap_start >= overlap_end:
            continue
        text_start = overlap_start - fragment.start
        text_end = overlap_end - fragment.start
        sliced.append(
            JumpFragment(
                kind=fragment.kind,
                text=fragment.text[text_start:text_end],
                start=overlap_start - sent_start,
                end=overlap_end - sent_start,
                href=fragment.href,
                anchor_id=fragment.anchor_id,
            )
        )
    return sliced


def collect_debug_spans(element, config: TagFilterConfig | None = None) -> list[DebugSpan]:
    """Return debug spans for visible text fragments under *element*."""

    config = config or TagFilterConfig()
    tree = element.getroottree()
    debug_spans: list[DebugSpan] = []

    for span in _iter_readable_text_parts(element, tree, config):
        policy = match_element_policy(span._node, config) if hasattr(span, '_node') else None
        text = '<break>' if span.source_kind == 'synthetic-break' else SentenceSplitter.normalize_text(span.text)
        if not text:
            continue
        debug_spans.append(
            DebugSpan(
                xpath=span.xpath,
                tag=_local_tag(getattr(span, '_tag', '')) or '',
                text_preview=text[:80],
                action=(policy.action.name if policy else get_extract_action(span._node, config).name) if hasattr(span, '_node') else '',
                policy_name=policy.name if policy else '',
            )
        )

    return debug_spans


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
    start_root = resolved['start'].get('root')
    end_root = resolved['end'].get('root')
    if not start or not end or start_root is None or end_root is None:
        return ''
    if start_root is not end_root:
        return ''
    if start.get('type') != 'text' or end.get('type') != 'text':
        return ''

    if start.get('node') is end.get('node'):
        spans = _collect_text_spans(start['node'], start_root.getroottree(), config)
        if not spans:
            return ''
        return SentenceSplitter.normalize_text(
            _extract_text_from_spans(
                spans,
                start['text_node_index'],
                start['offset'],
                end['text_node_index'],
                end['offset'],
            )
        )

    common = _lowest_common_block(start['node'], end['node'], config)
    if common is None:
        return ''

    spans = _collect_text_spans(common, start_root.getroottree(), config)
    if not spans:
        return ''

    start_abs = _span_absolute_position(spans, start['node'], start['text_node_index'], start['offset'])
    end_abs = _span_absolute_position(spans, end['node'], end['text_node_index'], end['offset'])
    if start_abs is None or end_abs is None or start_abs >= end_abs:
        return ''

    boundaries = _build_span_boundaries(spans)
    sliced = _slice_spans(boundaries, start_abs, end_abs)
    return SentenceSplitter.normalize_text(''.join(span.text for span in sliced))


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

    if spans and spans[-1].text.endswith(' ') and text.startswith(' '):
        text = text.lstrip()
    elif spans and _needs_inter_span_space(spans[-1].text, text):
        text = f' {text}'
    if not text:
        return

    span.text = text
    spans.append(span)


def _clone_span(span: TextSpan) -> TextSpan:
    clone = TextSpan(
        text=span.text,
        xpath=span.xpath,
        text_node_index=span.text_node_index,
        char_offset=span.char_offset,
        source_kind=span.source_kind,
        cfi_text_node_index=span.cfi_text_node_index,
        cfi_exact=span.cfi_exact,
    )
    if hasattr(span, '_node'):
        clone._node = span._node
    if hasattr(span, '_tag'):
        clone._tag = span._tag
    return clone


def _needs_inter_span_space(previous: str, current: str) -> bool:
    if not previous or not current:
        return False
    prev_char = previous[-1]
    curr_char = current[0]
    if prev_char.isspace() or curr_char.isspace():
        return False
    if re.match(r'[A-Za-z0-9]', prev_char) and re.match(r'[A-Za-z0-9]', curr_char):
        if len(previous) == 1 and previous.isupper() and current[:1].islower():
            return False
        if len(previous) > 1 or len(current) > 1:
            return True
    if prev_char in '.!?,;:)]}"”’' and re.match(r'[A-Za-z0-9]', curr_char):
        return True
    return False


def _direct_text_node_index(element, child=None) -> int:
    """Return the direct text node index within *element*."""

    if child is None:
        return 0
    element_children = [node for node in element if isinstance(node.tag, str)]
    return element_children.index(child) + 1


def _tail_text_node_index(element, child) -> int:
    count = 0
    for current in element:
        if isinstance(current.tag, str):
            count += 1
        if current is child:
            return count
    return count


def _child_anchor_index(element, child) -> int:
    count = 0
    for current in element:
        if current is child:
            return count
        if isinstance(current.tag, str):
            count += 1
    return count


def _make_span(text: str, xpath: str, text_node_index: int, anchor_tni: int, *, source_kind: str, exact: bool) -> TextSpan:
    span = TextSpan(
        text=text,
        xpath=xpath,
        text_node_index=text_node_index,
        char_offset=0,
        source_kind=source_kind,
        cfi_text_node_index=anchor_tni,
        cfi_exact=exact,
    )
    setattr(span, '_node', None)
    setattr(span, '_tag', '')
    return span


def _iter_readable_text_parts(
    element,
    tree,
    config: TagFilterConfig,
) -> Iterable[TextSpan]:
    """Yield readable text spans in DOM order for a block element."""

    def yield_text(node, *, text_node_index: int, anchor_tni: int, source_kind: str, exact: bool):
        text = node.text if source_kind == 'text' else ''
        span = _make_span(
            text=text,
            xpath=tree.getpath(node),
            text_node_index=text_node_index,
            anchor_tni=anchor_tni,
            source_kind=source_kind,
            exact=exact,
        )
        span._node = node
        span._tag = _local_tag(node.tag)
        yield span

    def yield_tail(parent, child, anchor_tni: int, exact: bool):
        if not child.tail:
            return
        span = _make_span(
            text=child.tail,
            xpath=tree.getpath(parent),
            text_node_index=_tail_text_node_index(parent, child),
            anchor_tni=anchor_tni,
            source_kind='tail',
            exact=exact,
        )
        span._node = parent
        span._tag = _local_tag(parent.tag)
        yield span

    def walk(node, anchor_tni: int):
        action = get_extract_action(node, config)
        if action == ExtractAction.SKIP_ENTIRE:
            return

        if action in {
            ExtractAction.KEEP_NORMAL,
            ExtractAction.KEEP_CHILDREN_ONLY,
            ExtractAction.KEEP_DIRECT_TEXT_ONLY,
            ExtractAction.BLOCK_BREAK,
            ExtractAction.STRUCTURAL_CONTAINER,
        } and node.text:
            yield from yield_text(
                node,
                text_node_index=0,
                anchor_tni=anchor_tni if node is not element else 0,
                source_kind='text',
                exact=node is element,
            )

        if action == ExtractAction.INLINE_BREAK:
            span = _make_span(
                text=config.inline_break_text,
                xpath=tree.getpath(node),
                text_node_index=0,
                anchor_tni=anchor_tni,
                source_kind='synthetic-break',
                exact=node is element,
            )
            span._node = node
            span._tag = _local_tag(node.tag)
            yield span
            return

        recurse_children = action not in {ExtractAction.SKIP_ENTIRE, ExtractAction.KEEP_DIRECT_TEXT_ONLY}
        if recurse_children:
            for child in node:
                if not isinstance(child.tag, str):
                    if child.tail:
                        yield from yield_tail(
                            node,
                            child,
                            _tail_text_node_index(node, child) if node is element else anchor_tni,
                            node is element,
                        )
                    continue

                child_action = get_extract_action(child, config)
                child_anchor = _child_anchor_index(node, child) if node is element else anchor_tni
                if child_action in {ExtractAction.BLOCK_BREAK, ExtractAction.STRUCTURAL_CONTAINER}:
                    if child.tail:
                        yield from yield_tail(
                            node,
                            child,
                            _tail_text_node_index(node, child) if node is element else anchor_tni,
                            node is element,
                        )
                    continue

                if child_action != ExtractAction.SKIP_ENTIRE:
                    yield from walk(child, child_anchor if node is element else anchor_tni)

                if child.tail:
                    yield from yield_tail(
                        node,
                        child,
                        _tail_text_node_index(node, child) if node is element else anchor_tni,
                        node is element,
                    )

    yield from walk(element, 0)


def _collect_text_spans(element, tree, config: TagFilterConfig) -> list[TextSpan]:
    """Collect normalized readable text spans for *element*."""

    raw_spans = list(_iter_readable_text_parts(element, tree, config))
    return _normalize_readable_spans(raw_spans, config)


def _prune_noise_spans(spans: list[TextSpan], config: TagFilterConfig) -> list[TextSpan]:
    return _normalize_readable_spans(spans, config)


def _normalize_readable_spans(spans: list[TextSpan], config: TagFilterConfig) -> list[TextSpan]:
    if not spans:
        return spans

    kept: list[TextSpan] = []
    for idx, span in enumerate(spans):
        text = SentenceSplitter.normalize_text(span.text)
        if _should_drop_standalone_span(spans, idx, text, config):
            continue
        kept.append(span)
    return _collapse_spans(kept)


def _collapse_spans(spans: Iterable[TextSpan]) -> list[TextSpan]:
    collapsed: list[TextSpan] = []
    for span in spans:
        _append_span(collapsed, _clone_span(span))
    return collapsed


def _should_drop_standalone_span(
    spans: list[TextSpan],
    idx: int,
    text: str,
    config: TagFilterConfig,
) -> bool:
    if spans[idx].source_kind == 'synthetic-break':
        return False
    if not text:
        return True
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in config.skip_line_patterns):
        prev_kind = spans[idx - 1].source_kind if idx > 0 else 'boundary'
        next_kind = spans[idx + 1].source_kind if idx + 1 < len(spans) else 'boundary'
        if prev_kind in {'synthetic-break', 'boundary'} or next_kind in {'synthetic-break', 'boundary'}:
            return True
    if config.drop_numeric_break_markers and re.fullmatch(r'[0-9]{1,4}(?:/[0-9]{1,4}){0,2}', text):
        prev_kind = spans[idx - 1].source_kind if idx > 0 else 'boundary'
        next_kind = spans[idx + 1].source_kind if idx + 1 < len(spans) else 'boundary'
        if prev_kind in {'synthetic-break', 'boundary'} and next_kind in {'synthetic-break', 'boundary'}:
            return True
    return False


def _trim_spans(
    spans: list[TextSpan],
) -> tuple[list[TextSpan], int, int, int, int]:
    """Trim leading and trailing whitespace while keeping source trace intact."""

    if not spans:
        return [], 0, 0, 0, 0

    trimmed = [_clone_span(span) for span in spans]
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
            lengths[span.cfi_text_node_index] = max(lengths.get(span.cfi_text_node_index, 0), len(span.text))
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
    paragraph_cfi: str,
    spans: list[TextSpan],
    sentences: list[str],
    paragraph_jump_fragments: list[JumpFragment],
    is_note_like: bool,
    alignment_role: str,
    paratext_kind: str,
    filter_reason: str,
) -> list[Segment]:
    """Map split sentences back to subsets of paragraph spans."""

    if not spans:
        return []

    full_text = ''.join(span.text for span in spans)
    parent_lengths = _parent_text_lengths(spans)
    boundaries = _build_span_boundaries(spans)
    ranges = _sentence_ranges(full_text, sentences)
    if not ranges:
        ranges = [(0, len(full_text), full_text)]

    segments: list[Segment] = []
    for sentence_idx, (sent_start, sent_end, sentence_text) in enumerate(ranges):
        sentence_spans = _slice_spans(boundaries, sent_start, sent_end)
        if not sentence_spans:
            continue
        sentence_jump_fragments = _slice_jump_fragments(paragraph_jump_fragments, sent_start, sent_end)

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
                text=sentence_text,
                cfi=cfi or '',
                chapter_idx=chapter_idx,
                paragraph_idx=paragraph_idx,
                sentence_idx=sentence_idx,
                paragraph_cfi=paragraph_cfi,
                text_start=sent_start,
                text_end=sent_end,
                raw_html=raw_html,
                element_xpath=element_xpath,
                has_jump_markup=bool(sentence_jump_fragments),
                is_note_like=is_note_like,
                alignment_role=alignment_role,
                paratext_kind=paratext_kind,
                filter_reason=filter_reason,
                jump_fragments=sentence_jump_fragments,
                spans=[_clone_span(span) for span in sentence_spans],
            )
        )

    return segments


def _build_span_boundaries(spans: list[TextSpan]) -> list[tuple[int, int, TextSpan]]:
    boundaries: list[tuple[int, int, TextSpan]] = []
    cursor = 0
    for span in spans:
        start = cursor
        cursor += len(span.text)
        boundaries.append((start, cursor, span))
    return boundaries


def _sentence_ranges(full_text: str, sentences: list[str]) -> list[tuple[int, int, str]]:
    ranges: list[tuple[int, int, str]] = []
    search_from = 0

    for sentence in sentences:
        if not sentence:
            continue
        sent_start = full_text.find(sentence, search_from)
        if sent_start < 0:
            stripped = sentence.strip()
            if stripped:
                sent_start = full_text.find(stripped, search_from)
                sentence = stripped if sent_start >= 0 else sentence
        if sent_start < 0:
            continue
        sent_end = sent_start + len(sentence)
        ranges.append((sent_start, sent_end, full_text[sent_start:sent_end]))
        search_from = sent_end

    if not ranges:
        return []

    merged: list[tuple[int, int, str]] = []
    for idx, (start, end, _) in enumerate(ranges):
        next_start = ranges[idx + 1][0] if idx + 1 < len(ranges) else len(full_text)
        adjusted_end = max(end, next_start if idx + 1 < len(ranges) else end)
        merged.append((start, adjusted_end, full_text[start:adjusted_end].strip()))
    return [item for item in merged if item[2]]


def _split_paragraph_sentences(
    spans: list[TextSpan],
    paragraph_text: str,
    splitter: SentenceSplitter,
) -> list[str]:
    if _prefer_line_break_segmentation(spans):
        sentences: list[str] = []
        for line in _line_chunks_from_spans(spans):
            normalized = SentenceSplitter.normalize_text(line)
            if not normalized:
                continue
            line_sentences = splitter.split(normalized)
            sentences.extend(line_sentences or [normalized])
        return sentences or [paragraph_text]
    return splitter.split(paragraph_text) or [paragraph_text]


def _prefer_line_break_segmentation(spans: list[TextSpan]) -> bool:
    break_count = sum(1 for span in spans if span.source_kind == 'synthetic-break')
    if break_count < 2:
        return False
    chunks = _line_chunks_from_spans(spans)
    if len(chunks) < 3:
        return False
    lengths = [len(SentenceSplitter.normalize_text(chunk)) for chunk in chunks if SentenceSplitter.normalize_text(chunk)]
    if not lengths:
        return False
    short_ratio = sum(1 for length in lengths if length <= 30) / len(lengths)
    avg_length = sum(lengths) / len(lengths)
    return short_ratio >= 0.5 or avg_length <= 35


def _line_chunks_from_spans(spans: list[TextSpan]) -> list[str]:
    chunks: list[str] = []
    parts: list[str] = []
    for span in spans:
        if span.source_kind == 'synthetic-break':
            chunk = ''.join(parts).strip()
            if chunk:
                chunks.append(chunk)
            parts = []
            continue
        parts.append(span.text)
    tail = ''.join(parts).strip()
    if tail:
        chunks.append(tail)
    return chunks


def _slice_spans(
    boundaries: list[tuple[int, int, TextSpan]],
    sent_start: int,
    sent_end: int,
) -> list[TextSpan]:
    """Return the subset of spans covered by a text range."""

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


def _lowest_common_block(start_node, end_node, config: TagFilterConfig):
    start_ancestors = []
    current = start_node
    while current is not None:
        if isinstance(current.tag, str) and is_block_element(current, config):
            start_ancestors.append(current)
        current = current.getparent()

    current = end_node
    while current is not None:
        if current in start_ancestors:
            return current
        current = current.getparent()
    return None


def _span_absolute_position(
    spans: list[TextSpan],
    target_node,
    target_tni: int,
    target_offset: int,
) -> int | None:
    cursor = 0
    for span in spans:
        if span.cfi_text_node_index is None:
            cursor += len(span.text)
            continue

        if span.cfi_exact and getattr(span, '_node', None) is target_node:
            if span.cfi_text_node_index == target_tni:
                span_start = span.char_offset
                span_end = span.char_offset + len(span.text)
                if span_start <= target_offset <= span_end:
                    return cursor + (target_offset - span_start)
        cursor += len(span.text)
    return None
