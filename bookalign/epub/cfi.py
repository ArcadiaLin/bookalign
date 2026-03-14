"""EPUB CFI 核心模块 — 解析、解析、生成、文本抽取。

从 epub/bookalign_cfi_v2.py 迁移并重构为干净的模块 API。
"""

import re
from typing import Optional, Any

from ebooklib import epub
from lxml import etree


# ═══════════════════════════════════ Parser ═══════════════════════════════════

class CFIParser:
    """Regex-based EPUB CFI parser.

    Parses CFI strings like ``epubcfi(/6/12!/4/2/12,/1:1,/3:8)``
    into structured dicts with parent/start/end paths.
    """

    def __init__(self):
        special_char = r'[\[\](),;=^]'
        unescaped_char = (
            rf'(?:(?!{special_char})'
            r'[\t\n\r -\ud7ff\ue000-\ufffd\U00010000-\U0010ffff])'
        )
        escaped_char = r'\^' + special_char[:-1] + '-]'
        chars = fr'(?:{unescaped_char}|(?:{escaped_char}))+'
        chars_no_space = chars.replace('0020', '0021')
        integer = r'(?:[1-9][0-9]*)|0'

        def c(x):
            return re.compile(x)

        self.step_pat = c(rf'/({integer})')
        self.id_assertion_pat = c(rf'\[({chars})\]')
        self.offset_pat = c(rf':({integer})')

        self.ta1_pat = c(rf'({chars})(?:,({chars})){{0,1}}')
        self.ta2_pat = c(rf',({chars})')
        self.parameter_pat = c(
            fr';({chars_no_space})=((?:{chars})(?:,(?:{chars}))*)'
        )
        self.csv_item_pat = c(rf'({chars})(?:,|$)')

        unescape_pat = c(fr'{escaped_char[:2]}({escaped_char[2:]})')
        self.unescape = lambda x: unescape_pat.sub(r'\1', x)

    def do_match(self, pat, raw):
        m = pat.match(raw)
        if m is not None:
            raw = raw[m.end():]
        return m, raw

    def parse_epubcfi(self, raw: str) -> dict[str, Any]:
        """Parse a full ``epubcfi(...)`` string into parent/start/end paths."""
        result: dict[str, Any] = {
            'parent': {},
            'start': {},
            'end': {},
            'is_range': False,
            'raw_tail': raw,
        }
        if not raw:
            return result

        if not raw.startswith('epubcfi(') or not raw.endswith(')'):
            return result

        raw = raw[len('epubcfi('):-1]
        parent_cfi, raw = self.parse_path(raw)
        if not parent_cfi:
            return result

        result['parent'] = parent_cfi
        result['raw_tail'] = raw

        if raw.startswith(','):
            start_cfi, raw = self.parse_path(raw[1:])
            if not start_cfi:
                return result

            if not raw.startswith(','):
                return result

            end_cfi, raw = self.parse_path(raw[1:])
            if not end_cfi:
                return result

            result['start'] = start_cfi
            result['end'] = end_cfi
            result['is_range'] = True
            result['raw_tail'] = raw

        return result

    def parse_path(self, raw):
        path: dict[str, Any] = {'steps': []}
        raw = self._parse_path(raw, path)
        if not path['steps']:
            path = {}
        return path, raw

    def _parse_path(self, raw, ans):
        m, raw = self.do_match(self.step_pat, raw)
        if m is None:
            return raw

        ans['steps'].append({'num': int(m.group(1))})

        m, raw = self.do_match(self.id_assertion_pat, raw)
        if m is not None:
            ans['steps'][-1]['id'] = self.unescape(m.group(1))

        if raw.startswith('!'):
            ans['redirect'] = r = {'steps': []}
            return self._parse_path(raw[1:], r)

        remaining_raw = self.parse_offset(raw, ans['steps'][-1])
        return (
            self._parse_path(raw, ans)
            if remaining_raw is None
            else remaining_raw
        )

    def parse_offset(self, raw, ans):
        m, raw = self.do_match(self.offset_pat, raw)
        if m is not None:
            ans['offset'] = int(m.group(1))
            return self.parse_assertion(raw, ans)
        return None

    def parse_assertion(self, raw, ans):
        """Parse text assertion ``[before,after]`` after an offset."""
        original_raw = raw
        if not raw.startswith('['):
            return original_raw

        raw = raw[1:]
        ta: dict[str, str] = {}

        m, raw = self.do_match(self.ta1_pat, raw)
        if m is not None:
            before, after = m.groups()
            ta['before'] = self.unescape(before)
            if after is not None:
                ta['after'] = self.unescape(after)
        else:
            m, raw = self.do_match(self.ta2_pat, raw)
            if m is not None:
                ta['after'] = self.unescape(m.group(1))

        if not raw.startswith(']'):
            return original_raw

        if ta:
            ans['assertion'] = ta
        return raw[1:]


# ═══════════════════════════════ Spine helpers ════════════════════════════════

def _normalize_spine_entry(entry) -> Optional[str]:
    """Extract item ID from various spine entry formats."""
    if isinstance(entry, tuple):
        return entry[0]
    if isinstance(entry, str):
        return entry
    if hasattr(entry, 'id'):
        return entry.id
    if hasattr(entry, 'get_id'):
        return entry.get_id()
    return None


def _even_step_index(num: int) -> Optional[int]:
    """Convert even CFI step number to zero-based index: /2->0, /4->1, /6->2."""
    if not isinstance(num, int) or num < 2 or num % 2 != 0:
        return None
    return num // 2 - 1


def resolve_spine_item(
    cfi_dict: dict[str, Any], book: epub.EpubBook
) -> Optional[epub.EpubItem]:
    """Resolve package-level CFI steps to a spine item.

    Only supports ``/6/N`` paths (spine -> itemref).
    """
    steps = cfi_dict.get('steps', [])
    if len(steps) < 2:
        return None

    first_idx = _even_step_index(steps[0].get('num'))
    second_idx = _even_step_index(steps[1].get('num'))

    if first_idx != 2:  # /6 -> spine
        return None
    if second_idx is None:
        return None
    if second_idx >= len(book.spine):
        return None

    spine_entry = book.spine[second_idx]
    item_id = _normalize_spine_entry(spine_entry)
    if not item_id:
        return None

    return book.get_item_with_id(item_id)


def parse_item_xml(item: epub.EpubItem):
    """Parse EpubItem content into an lxml element tree root."""
    content = item.get_content()
    parser = etree.XMLParser(recover=True)
    return etree.fromstring(content, parser=parser)


# ═══════════════════════════════ DOM navigation ══════════════════════════════

def _elem_children(node) -> list:
    """Return only real element children (skip comments, PIs)."""
    return [child for child in node if isinstance(child.tag, str)]


def _resolve_elem_step(node, num: int):
    """Resolve an even-numbered CFI step to a child element."""
    idx = _even_step_index(num)
    if idx is None:
        return None
    children = _elem_children(node)
    if idx >= len(children):
        return None
    return children[idx]


def _all_text(node) -> str:
    """Collect all text content from a node recursively."""
    return ''.join(node.itertext())


def _check_assertion(node, assertion: Optional[dict[str, Any]]) -> bool:
    """Loose assertion check: verify before/after text exists in node."""
    if not assertion:
        return True
    text = _all_text(node)
    before = assertion.get('before')
    after = assertion.get('after')
    if before and before not in text:
        return False
    if after and after not in text:
        return False
    return True


def resolve_dom_steps(
    root, redirect: dict[str, Any]
) -> Optional[dict[str, Any]]:
    """Walk the document DOM according to CFI redirect steps.

    - Even step: navigate to child element
    - Odd step (terminal): select a text node within current element
      /1 -> text_node_index 0, /3 -> 1, /(2n+1) -> n
    """
    if not redirect:
        return None

    steps = redirect.get('steps', [])
    if not steps:
        return None

    node = root

    for i, step in enumerate(steps):
        num = step.get('num')
        node_id = step.get('id')

        if isinstance(num, int) and num % 2 == 0:
            next_node = _resolve_elem_step(node, num)
            if next_node is None:
                return None

            if node_id is not None:
                actual_id = next_node.get('id')
                if actual_id != node_id:
                    raise ValueError(
                        f'ID assertion failed at step {i}: '
                        f'expected {node_id}, got {actual_id}'
                    )

            node = next_node
            continue

        if isinstance(num, int) and num % 2 == 1:
            if i == len(steps) - 1:
                text_node_index = (num - 1) // 2
                return {
                    'node': node,
                    'text_node_index': text_node_index,
                    'offset': step.get('offset', 0),
                    'assertion': step.get('assertion'),
                    'terminal_step': step,
                }
            return None

        return None

    last_step = steps[-1]
    return {
        'node': node,
        'text_node_index': None,
        'offset': last_step.get('offset', 0),
        'assertion': last_step.get('assertion'),
        'terminal_step': last_step,
    }


# ═══════════════════════════ Text position resolution ════════════════════════

def _iter_text_nodes(element):
    """Yield ``(owner, kind, text)`` for direct text segments in order.

    Index 0: ``(element, 'text', element.text)``
    Index 1+: ``(child_i, 'tail', child_i.tail)``
    """
    yield (element, 'text', element.text or '')
    for child in element:
        yield (child, 'tail', child.tail or '')


def resolve_text_pos(resolved: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Resolve a DOM step result to a precise text position."""
    if not resolved:
        return None

    node = resolved['node']
    offset = resolved.get('offset')
    assertion = resolved.get('assertion')
    text_node_index = resolved.get('text_node_index')

    if offset is None and text_node_index is None:
        if assertion and not _check_assertion(node, assertion):
            return None
        return {
            'type': 'element',
            'node': node,
            'assertion': assertion,
        }

    if offset is not None and offset < 0:
        return None

    segments = list(_iter_text_nodes(node))

    if text_node_index is not None:
        if text_node_index >= len(segments):
            return None
        owner, kind, text = segments[text_node_index]
        actual_offset = offset if offset is not None else 0
        if actual_offset > len(text):
            return None

        if assertion:
            before = assertion.get('before')
            after = assertion.get('after')
            if before is not None and not text[:actual_offset].endswith(before):
                return None
            if after is not None and not text[actual_offset:].startswith(after):
                return None

        return {
            'type': 'text',
            'node': node,
            'text_node_index': text_node_index,
            'owner': owner,
            'kind': kind,
            'text': text,
            'offset': actual_offset,
            'assertion': assertion,
        }

    # Fallback: no text_node_index — cumulate across all segments
    remain = offset
    for seg_idx, (owner, kind, text) in enumerate(segments):
        if remain <= len(text):
            return {
                'type': 'text',
                'node': node,
                'text_node_index': seg_idx,
                'owner': owner,
                'kind': kind,
                'text': text,
                'offset': remain,
                'assertion': assertion,
            }
        remain -= len(text)

    return None


# ═══════════════════════════════ CFI resolution ══════════════════════════════

def _resolve_redirect(root, redirect):
    """Resolve redirect steps + text position against a pre-parsed root."""
    if not redirect:
        return None
    dom_resolved = resolve_dom_steps(root, redirect)
    if dom_resolved is None:
        return None
    return resolve_text_pos(dom_resolved)


def resolve_path(
    path_cfi: dict[str, Any],
    book: epub.EpubBook,
    _root=None,
) -> Optional[dict[str, Any]]:
    """Resolve a single (non-range) CFI path to item + target."""
    epub_item = resolve_spine_item(path_cfi, book)
    if epub_item is None:
        return None

    root = _root if _root is not None else parse_item_xml(epub_item)
    redirect = path_cfi.get('redirect')

    if not redirect:
        return {'item': epub_item, 'root': root, 'target': None}

    target = _resolve_redirect(root, redirect)
    return {'item': epub_item, 'root': root, 'target': target}


def _merge_paths(
    parent: dict[str, Any], child: dict[str, Any]
) -> dict[str, Any]:
    """Merge a range's parent path with a start/end suffix into a full path."""
    merged: dict[str, Any] = {
        'steps': list(parent.get('steps', [])),
    }

    parent_redirect = parent.get('redirect')
    child_steps = child.get('steps', [])

    if parent_redirect:
        merged['redirect'] = {
            'steps': list(parent_redirect.get('steps', []))
            + list(child_steps)
        }
    else:
        merged['steps'] += list(child_steps)

    if child.get('redirect'):
        if merged.get('redirect'):
            merged['redirect']['steps'].extend(
                child['redirect'].get('steps', [])
            )
        else:
            merged['redirect'] = {
                'steps': list(child['redirect'].get('steps', []))
            }

    return merged


def resolve_cfi(
    cfi_str: str, book: epub.EpubBook
) -> Optional[dict[str, Any]]:
    """Resolve a CFI string (simple or range) to targets.

    For range CFI ``epubcfi(parent,start,end)``: merges parent with
    start/end suffixes.
    """
    parsed = CFIParser().parse_epubcfi(cfi_str)
    parent = parsed.get('parent')
    if not parent:
        return None

    if not parsed.get('is_range'):
        return resolve_path(parent, book)

    start = parsed.get('start')
    end = parsed.get('end')
    if not start or not end:
        return None

    start_path = _merge_paths(parent, start)
    end_path = _merge_paths(parent, end)

    epub_item = resolve_spine_item(start_path, book)
    if epub_item is None:
        return None
    root = parse_item_xml(epub_item)

    start_target = resolve_path(start_path, book, _root=root)
    end_target = resolve_path(end_path, book, _root=root)

    if start_target is None or end_target is None:
        return None

    return {
        'type': 'range',
        'start': start_target,
        'end': end_target,
    }


# ═══════════════════════════════ Text extraction ═════════════════════════════

def _local_tag(tag) -> str:
    """Strip namespace from an lxml tag: ``'{ns}name'`` -> ``'name'``."""
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}')[1]
    return tag


_SKIP_TAGS = frozenset({'rt', 'rp'})
_INCLUDE_CHILD_TEXT_TAGS = frozenset({'ruby'})


def _child_readable_text(element, skip_tags=_SKIP_TAGS) -> str:
    """Get readable text from a child element, skipping ``<rt>`` content."""
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in element:
        tag = _local_tag(child.tag)
        if isinstance(tag, str) and tag not in skip_tags:
            parts.append(_child_readable_text(child, skip_tags))
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts)


def _readable_segments(
    element,
    skip_tags=_SKIP_TAGS,
    include_child_text_tags=_INCLUDE_CHILD_TEXT_TAGS,
) -> list[dict[str, Any]]:
    """Build ordered readable text segments for an element.

    Returns list of dicts with keys:
      - ``text``: the text content
      - ``type``: ``'parent'`` (parent-level text node) or ``'child'``
      - ``tni``: text node index (for ``'parent'`` type)
      - ``after_tni``: preceding parent text node index (for ``'child'`` type)
    """
    segs: list[dict[str, Any]] = []
    segs.append({'text': element.text or '', 'type': 'parent', 'tni': 0})

    for i, child in enumerate(element):
        tni = i + 1
        tag = _local_tag(child.tag)
        if isinstance(tag, str) and tag in include_child_text_tags:
            ct = _child_readable_text(child, skip_tags)
            if ct:
                segs.append({'text': ct, 'type': 'child', 'after_tni': i})

        segs.append({'text': child.tail or '', 'type': 'parent', 'tni': tni})

    return segs


def _extract_readable_text(
    element, start_tni: int, start_off: int, end_tni: int, end_off: int,
) -> str:
    """Extract readable text between two parent text node positions."""
    segs = _readable_segments(element)
    parts: list[str] = []

    for seg in segs:
        if seg['type'] == 'parent':
            tni = seg['tni']
            text = seg['text']
            if tni < start_tni or tni > end_tni:
                continue
            if tni == start_tni and tni == end_tni:
                parts.append(text[start_off:end_off])
            elif tni == start_tni:
                parts.append(text[start_off:])
            elif tni == end_tni:
                parts.append(text[:end_off])
            else:
                parts.append(text)
        else:
            after_tni = seg['after_tni']
            if start_tni <= after_tni < end_tni:
                parts.append(seg['text'])

    return ''.join(parts)


def extract_range_text(range_result: dict) -> Optional[str]:
    """Extract all readable text between two resolved range endpoints."""
    if not range_result or range_result.get('type') != 'range':
        return None

    start_res = range_result['start']
    end_res = range_result['end']

    start_target = start_res.get('target')
    end_target = end_res.get('target')

    if not start_target or not end_target:
        return None
    if start_target.get('type') != 'text' or end_target.get('type') != 'text':
        return None

    start_node = start_target['node']
    end_node = end_target['node']
    start_tni = start_target['text_node_index']
    end_tni = end_target['text_node_index']
    start_off = start_target['offset']
    end_off = end_target['offset']

    if start_node is end_node:
        return _extract_readable_text(
            start_node, start_tni, start_off, end_tni, end_off
        )

    # Different parent elements — walk the tree
    start_root = start_res.get('root')
    if start_root is None:
        return None

    parts: list[str] = []
    collecting = False

    for elem in start_root.iter():
        if not isinstance(elem.tag, str):
            continue

        if elem is start_node:
            segs = _readable_segments(elem)
            last_parent_tni = max(
                s['tni'] for s in segs if s['type'] == 'parent'
            )
            last_parent_text = [
                s for s in segs if s['type'] == 'parent'
            ][-1]['text']
            parts.append(
                _extract_readable_text(
                    elem, start_tni, start_off,
                    last_parent_tni, len(last_parent_text),
                )
            )
            collecting = True
            continue

        if elem is end_node:
            parts.append(
                _extract_readable_text(elem, 0, 0, end_tni, end_off)
            )
            break

        if collecting:
            parent = elem.getparent()
            if parent is not None and parent is start_node:
                continue
            if len(_elem_children(elem)) > 0:
                continue
            segs = _readable_segments(elem)
            for seg in segs:
                parts.append(seg['text'])

    return ''.join(parts)


# ═══════════════════════════════ CFI generation ══════════════════════════════

def _build_dom_path(root, target_elem) -> Optional[list[tuple]]:
    """Build path from root to target as ``[(parent, child_index), ...]``."""
    parent_map: dict = {}
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        for child in elem:
            if isinstance(child.tag, str):
                parent_map[child] = elem

    if target_elem is root:
        return []

    path: list[tuple] = []
    current = target_elem
    while current in parent_map:
        parent = parent_map[current]
        children = _elem_children(parent)
        idx = None
        for i, ch in enumerate(children):
            if ch is current:
                idx = i
                break
        if idx is None:
            return None
        path.append((parent, idx))
        current = parent

    if current is not root:
        return None

    path.reverse()
    return path


def _find_text_in_element(
    element, text: str
) -> Optional[tuple[int, int, int, int]]:
    """Search for *text* in an element's readable text.

    Returns ``(start_tni, start_off, end_tni, end_off)`` mapped to parent
    text node positions, or ``None`` if not found.  Positions inside child
    element text are snapped to the nearest parent text node boundary.
    """
    segs = _readable_segments(element)
    readable = ''.join(s['text'] for s in segs)
    pos = readable.find(text)
    if pos == -1:
        return None

    end_pos = pos + len(text)

    boundaries: list[tuple[int, int, dict]] = []
    cum = 0
    for seg in segs:
        seg_len = len(seg['text'])
        boundaries.append((cum, cum + seg_len, seg))
        cum += seg_len

    def map_pos(p, is_end):
        for i, (start, end, seg) in enumerate(boundaries):
            if not (start <= p <= end):
                continue
            if start == end and p == start:
                if seg['type'] == 'parent':
                    return (seg['tni'], 0)
                continue
            if seg['type'] == 'parent':
                return (seg['tni'], p - start)
            else:
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

    start_result = map_pos(pos, is_end=False)
    end_result = map_pos(end_pos, is_end=True)

    if start_result is None or end_result is None:
        return None

    return (*start_result, *end_result)


def _spine_index_of_item(
    book: epub.EpubBook, item: epub.EpubItem
) -> Optional[int]:
    """Find the spine index of an item."""
    item_id = item.get_id()
    for i, entry in enumerate(book.spine):
        entry_id = _normalize_spine_entry(entry)
        if entry_id == item_id:
            return i
    return None


def generate_range_cfi(
    book: epub.EpubBook, item: epub.EpubItem, text: str
) -> Optional[str]:
    """Generate a range CFI for *text* found in *item*.

    Searches readable text of each element for the target text.
    Returns ``epubcfi(parent,start_suffix,end_suffix)`` or ``None``.
    """
    root = parse_item_xml(item)
    spine_idx = _spine_index_of_item(book, item)
    if spine_idx is None:
        return None

    pkg_step2 = (spine_idx + 1) * 2

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue

        found = _find_text_in_element(elem, text)
        if found is None:
            continue

        start_tni, start_off, end_tni, end_off = found
        return _build_cfi_string(
            root, elem, pkg_step2, start_tni, start_off, end_tni, end_off
        )

    return None


def generate_cfi_for_text_range(
    book: epub.EpubBook,
    item: epub.EpubItem,
    element,
    start_tni: int,
    start_off: int,
    end_tni: int,
    end_off: int,
    _root=None,
) -> Optional[str]:
    """Generate a range CFI from already-known text node positions.

    Used internally by the extractor when the element and text positions
    are already computed (avoids re-searching).
    """
    spine_idx = _spine_index_of_item(book, item)
    if spine_idx is None:
        return None

    root = _root if _root is not None else parse_item_xml(item)
    pkg_step2 = (spine_idx + 1) * 2

    return _build_cfi_string(
        root, element, pkg_step2, start_tni, start_off, end_tni, end_off
    )


def _build_cfi_string(
    root, elem, pkg_step2: int,
    start_tni: int, start_off: int,
    end_tni: int, end_off: int,
) -> Optional[str]:
    """Build a range CFI string from resolved positions."""
    dom_path = _build_dom_path(root, elem)
    if dom_path is None:
        return None

    elem_steps = []
    for _, child_idx in dom_path:
        step_num = (child_idx + 1) * 2
        elem_steps.append(step_num)

    start_odd = start_tni * 2 + 1
    end_odd = end_tni * 2 + 1

    elem_path_str = ''.join(f'/{s}' for s in elem_steps)
    parent_str = f'/6/{pkg_step2}!{elem_path_str}'
    start_str = f'/{start_odd}:{start_off}'
    end_str = f'/{end_odd}:{end_off}'

    return f'epubcfi({parent_str},{start_str},{end_str})'
