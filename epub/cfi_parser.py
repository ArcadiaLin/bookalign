import re
from typing import Optional, Dict, Any, List, Tuple, Iterator

from ebooklib import epub
from lxml import etree


# =========================== Parser ===========================

class CFIParser:
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
        self.parameter_pat = c(fr';({chars_no_space})=((?:{chars})(?:,(?:{chars}))*)')
        self.csv_item_pat = c(rf'({chars})(?:,|$)')

        unescape_pat = c(fr'{escaped_char[:2]}({escaped_char[2:]})')
        self.unescape = lambda x: unescape_pat.sub(r'\1', x)

    def do_match(self, pat, raw):
        m = pat.match(raw)
        if m is not None:
            raw = raw[m.end():]
        return m, raw

    def parse_epubcfi(self, raw: str) -> Dict[str, Any]:
        """Parse a full epubcfi(...) string into parent/start/end paths."""
        result = {
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
        path = {'steps': []}
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
        return self._parse_path(raw, ans) if remaining_raw is None else remaining_raw

    def parse_offset(self, raw, ans):
        m, raw = self.do_match(self.offset_pat, raw)
        if m is not None:
            ans['offset'] = int(m.group(1))
            return self.parse_assertion(raw, ans)
        return None

    def parse_assertion(self, raw, ans):
        """Parse text assertion [before,after] after an offset."""
        original_raw = raw
        if not raw.startswith('['):
            return original_raw

        raw = raw[1:]
        ta = {}

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


# =========================== Package-level ===========================

def _normalize_spine_entry(entry):
    """Extract item ID from various spine entry formats."""
    if isinstance(entry, tuple):
        return entry[0]
    if isinstance(entry, str):
        return entry
    if hasattr(entry, "id"):
        return entry.id
    if hasattr(entry, "get_id"):
        return entry.get_id()
    return None


def _even_step_index(num: int) -> Optional[int]:
    """Convert even CFI step number to zero-based index: /2->0, /4->1, /6->2."""
    if not isinstance(num, int) or num < 2 or num % 2 != 0:
        return None
    return num // 2 - 1


def resolve_spine_item(cfi_dict: Dict[str, Any], book: epub.EpubBook) -> Optional[epub.EpubItem]:
    """Resolve package-level CFI steps to a spine item.
    Only supports /6/N paths (spine -> itemref).
    /6 -> spine, /6/2 -> 1st itemref, /6/4 -> 2nd itemref, etc.
    """
    steps = cfi_dict.get('steps', [])
    if len(steps) < 2:
        return None

    first_num = steps[0].get('num')
    second_num = steps[1].get('num')

    first_idx = _even_step_index(first_num)
    second_idx = _even_step_index(second_num)

    # Package children: /2->metadata, /4->manifest, /6->spine
    if first_idx != 2:
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


# =========================== Document-level ===========================

def _elem_children(node) -> List[Any]:
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


def _check_assertion(node, assertion: Optional[Dict[str, Any]]) -> bool:
    """Loose assertion check: verify that before/after text exists somewhere in node."""
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


def resolve_dom_steps(root, redirect: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Walk the document DOM according to CFI redirect steps.
    - Even step: navigate to child element
    - Even step with id: verify id assertion on child
    - Odd step (terminal only): select a text node within current element
      /1 -> text_node_index 0 (element.text)
      /3 -> text_node_index 1 (first child's tail)
      /(2n+1) -> text_node_index n
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
                        f'ID assertion failed at step {i}: expected {node_id}, got {actual_id}'
                    )

            node = next_node
            continue

        if isinstance(num, int) and num % 2 == 1:
            # Odd step: must be terminal, selects a text node
            if i == len(steps) - 1:
                text_node_index = (num - 1) // 2  # /1->0, /3->1, /5->2
                return {
                    'node': node,
                    'text_node_index': text_node_index,
                    'offset': step.get('offset', 0),
                    'assertion': step.get('assertion'),
                    'terminal_step': step,
                }
            return None

        return None

    # Ended on an even step (element node, no text node selection)
    last_step = steps[-1]
    return {
        'node': node,
        'text_node_index': None,
        'offset': last_step.get('offset', 0),
        'assertion': last_step.get('assertion'),
        'terminal_step': last_step,
    }


# =========================== Offset / Assertion ===========================

def _iter_text_nodes(element) -> Iterator[Tuple[Any, str, str]]:
    """Yield direct text segments in order:
    index 0: (element, 'text', element.text)
    index 1: (child0, 'tail', child0.tail)
    index 2: (child1, 'tail', child1.tail)
    ...
    Segments with empty/None text are still yielded (with empty string)
    so that indices stay aligned with CFI odd step numbering.
    """
    yield (element, 'text', element.text or '')
    for child in element:
        yield (child, 'tail', child.tail or '')


def resolve_text_pos(resolved: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resolve a DOM step result to a precise text position.
    Uses text_node_index to jump directly to the correct text segment
    instead of cumulating offsets across all segments.
    """
    if not resolved:
        return None

    node = resolved['node']
    offset = resolved.get('offset')
    assertion = resolved.get('assertion')
    text_node_index = resolved.get('text_node_index')

    # No offset means we target the element itself
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

    # If text_node_index is set, jump directly to that segment
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

    # Fallback: no text_node_index (even step with offset) - cumulate across all segments
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


# =========================== Single CFI Resolution ===========================

def _resolve_redirect(root, redirect):
    """Resolve redirect steps + text position against a pre-parsed root."""
    if not redirect:
        return None
    dom_resolved = resolve_dom_steps(root, redirect)
    if dom_resolved is None:
        return None
    return resolve_text_pos(dom_resolved)


def resolve_path(path_cfi: Dict[str, Any], book: epub.EpubBook,
                 _root=None) -> Optional[Dict[str, Any]]:
    """Resolve a single (non-range) CFI path to item + target.
    If _root is provided, reuse it instead of parsing XML again.
    """
    epub_item = resolve_spine_item(path_cfi, book)
    if epub_item is None:
        return None

    root = _root if _root is not None else parse_item_xml(epub_item)
    redirect = path_cfi.get('redirect')

    if not redirect:
        return {
            'item': epub_item,
            'root': root,
            'target': None,
        }

    target = _resolve_redirect(root, redirect)
    return {
        'item': epub_item,
        'root': root,
        'target': target,
    }


# =========================== Range CFI ===========================

def resolve_cfi(cfi_str: str, book: epub.EpubBook) -> Optional[Dict[str, Any]]:
    """Resolve a CFI string (simple or range) to targets.
    For range CFI epubcfi(parent,start,end): merges parent with start/end suffixes.
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

    # Resolve item and parse XML once, shared between start and end
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


def _merge_paths(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a range's parent path with a start/end suffix into a full path."""
    merged = {
        'steps': list(parent.get('steps', [])),
    }

    parent_redirect = parent.get('redirect')
    child_steps = child.get('steps', [])

    if parent_redirect:
        merged['redirect'] = {
            'steps': list(parent_redirect.get('steps', [])) + list(child_steps)
        }
    else:
        merged['steps'] += list(child_steps)

    if child.get('redirect'):
        if merged.get('redirect'):
            merged['redirect']['steps'].extend(child['redirect'].get('steps', []))
        else:
            merged['redirect'] = {
                'steps': list(child['redirect'].get('steps', []))
            }

    return merged


# =========================== Text Extraction ===========================

def _local_tag(tag):
    """Strip namespace from an lxml tag: '{ns}name' -> 'name'."""
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}')[1]
    return tag


_SKIP_TAGS = frozenset({'rt', 'rp'})
_INCLUDE_CHILD_TEXT_TAGS = frozenset({'ruby'})


def _child_readable_text(element) -> str:
    """Get readable text from a child element, skipping <rt> content."""
    parts = []
    if element.text:
        parts.append(element.text)
    for child in element:
        tag = _local_tag(child.tag)
        if isinstance(tag, str) and tag not in _SKIP_TAGS:
            parts.append(_child_readable_text(child))
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts)


def _readable_segments(element) -> List[Dict[str, Any]]:
    """Build ordered readable text segments for an element.

    Returns list of dicts, each with:
      - 'text': the text content
      - 'type': 'parent' (parent-level text node) or 'child' (child element inner text)
      - 'tni': text node index (for 'parent' type)
      - 'after_tni': preceding parent text node index (for 'child' type)

    Parent text nodes: element.text (tni=0), child0.tail (tni=1), child1.tail (tni=2), ...
    Child readable text: inner text of each child element (excluding <rt>).
    Order matches document order: parent[0], child_text[0], parent[1], child_text[1], ...
    """
    segs = []
    segs.append({'text': element.text or '', 'type': 'parent', 'tni': 0})

    for i, child in enumerate(element):
        tni = i + 1  # parent text node index for this child's tail

        # Only include child readable text from <ruby> elements (base characters).
        # Skip annotation children like <span class="super"> (footnote markers).
        tag = _local_tag(child.tag)
        if isinstance(tag, str) and tag in _INCLUDE_CHILD_TEXT_TAGS:
            ct = _child_readable_text(child)
            if ct:
                segs.append({'text': ct, 'type': 'child', 'after_tni': i})

        # Parent text node: child.tail
        segs.append({'text': child.tail or '', 'type': 'parent', 'tni': tni})

    return segs


def _extract_readable_text(element, start_tni: int, start_off: int,
                           end_tni: int, end_off: int) -> str:
    """Extract readable text between two parent text node positions in an element.

    Includes child element readable text (excluding <rt>) that sits between
    the start and end parent text nodes.
    """
    segs = _readable_segments(element)
    parts = []

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
            # Child readable text, sits between parent node after_tni and after_tni+1
            after_tni = seg['after_tni']
            if start_tni <= after_tni < end_tni:
                parts.append(seg['text'])

    return ''.join(parts)


def extract_range_text(range_result: dict) -> Optional[str]:
    """Extract all readable text between two resolved range endpoints.
    Includes child element text (excluding <rt> annotations) between parent text nodes.
    """
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
        return _extract_readable_text(start_node, start_tni, start_off, end_tni, end_off)

    # Different parent elements - walk the tree
    start_root = start_res.get('root')
    if start_root is None:
        return None

    parts = []
    collecting = False

    for elem in start_root.iter():
        if not isinstance(elem.tag, str):
            continue

        if elem is start_node:
            segs = _readable_segments(elem)
            last_parent_tni = max(s['tni'] for s in segs if s['type'] == 'parent')
            last_parent_len = len([s for s in segs if s['type'] == 'parent'][-1]['text'])
            parts.append(_extract_readable_text(
                elem, start_tni, start_off, last_parent_tni, last_parent_len))
            collecting = True
            continue

        if elem is end_node:
            parts.append(_extract_readable_text(elem, 0, 0, end_tni, end_off))
            break

        if collecting:
            parent = elem.getparent()
            if parent is not None and parent is start_node:
                continue
            has_children = len(_elem_children(elem)) > 0
            if not has_children:
                continue
            segs = _readable_segments(elem)
            for seg in segs:
                parts.append(seg['text'])

    return ''.join(parts)


# =========================== CFI Generation ===========================

def _build_dom_path(root, target_elem) -> Optional[List[Tuple[Any, int]]]:
    """Build path from root to target as list of (parent, child_index) pairs.
    child_index is the position among element children (0-based).
    """
    # BFS/DFS to find path
    parent_map = {}
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        for child in elem:
            if isinstance(child.tag, str):
                parent_map[child] = elem

    if target_elem is root:
        return []

    # Build path from target back to root
    path = []
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


def _find_text_in_element(element, text: str) -> Optional[Tuple[int, int, int, int]]:
    """Search for text in an element's readable text (including child text, excluding <rt>).

    Returns (start_text_node_idx, start_offset, end_text_node_idx, end_offset)
    mapped to parent text node positions, or None if not found.

    When the found position falls inside child element text, it snaps:
    - start: to end of preceding parent text node
    - end: to start of following parent text node
    This ensures the CFI range brackets all the readable text including child content.
    """
    segs = _readable_segments(element)
    readable = ''.join(s['text'] for s in segs)
    pos = readable.find(text)
    if pos == -1:
        return None

    end_pos = pos + len(text)

    # Build cumulative boundaries: (cum_start, cum_end, seg)
    boundaries = []
    cum = 0
    for seg in segs:
        seg_len = len(seg['text'])
        boundaries.append((cum, cum + seg_len, seg))
        cum += seg_len

    def map_pos(p, is_end):
        """Map a readable text position to (parent_tni, offset).
        is_end=False: snap child positions backward to preceding parent's end.
        is_end=True: snap child positions forward to following parent's start.
        """
        for i, (start, end, seg) in enumerate(boundaries):
            if not (start <= p <= end):
                continue
            if start == end and p == start:
                # Empty segment at boundary — prefer non-empty or parent segments
                if seg['type'] == 'parent':
                    return (seg['tni'], 0)
                continue

            if seg['type'] == 'parent':
                return (seg['tni'], p - start)
            else:
                # Position in child text — snap to nearest parent boundary
                if not is_end:
                    # Snap backward: end of preceding parent
                    for j in range(i - 1, -1, -1):
                        if boundaries[j][2]['type'] == 'parent':
                            s = boundaries[j][2]
                            return (s['tni'], len(s['text']))
                else:
                    # Snap forward: start of following parent
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


def _spine_index_of_item(book: epub.EpubBook, item: epub.EpubItem) -> Optional[int]:
    """Find the spine index of an item."""
    item_id = item.get_id()
    for i, entry in enumerate(book.spine):
        entry_id = _normalize_spine_entry(entry)
        if entry_id == item_id:
            return i
    return None


def generate_range_cfi(book: epub.EpubBook, item: epub.EpubItem, text: str) -> Optional[str]:
    """Generate a range CFI for a given text string found in an item.

    Searches parent-level text nodes of each element for the target text.
    Returns epubcfi(parent,start_suffix,end_suffix) or None if not found.
    """
    root = parse_item_xml(item)
    spine_idx = _spine_index_of_item(book, item)
    if spine_idx is None:
        return None

    # Package-level steps: /6 (spine) / (spine_idx+1)*2 (itemref)
    pkg_step2 = (spine_idx + 1) * 2

    # Search every element for the text
    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue

        found = _find_text_in_element(elem, text)
        if found is None:
            continue

        start_tni, start_off, end_tni, end_off = found

        # Build DOM path to this element
        dom_path = _build_dom_path(root, elem)
        if dom_path is None:
            continue

        # Build element path steps (even numbers)
        elem_steps = []
        for _, child_idx in dom_path:
            step_num = (child_idx + 1) * 2
            elem_steps.append(step_num)

        # Convert text node indices to odd step numbers: index n -> step (2n+1)
        start_odd = start_tni * 2 + 1
        end_odd = end_tni * 2 + 1

        # Build the full start and end redirect paths
        # redirect steps = elem_steps + terminal odd step with offset
        # Parent path: /6/N!/elem_steps...
        # Start suffix: /start_odd:start_off
        # End suffix: /end_odd:end_off

        # Factor: parent = /6/N! + common elem steps
        # start suffix = /start_odd:start_off
        # end suffix = /end_odd:end_off

        # Build strings
        elem_path_str = ''.join(f'/{s}' for s in elem_steps)
        parent_str = f'/6/{pkg_step2}!{elem_path_str}'
        start_str = f'/{start_odd}:{start_off}'
        end_str = f'/{end_odd}:{end_off}'

        return f'epubcfi({parent_str},{start_str},{end_str})'

    return None


# =========================== Debug / Tests ===========================

if __name__ == '__main__':
    import sys

    test_ebook = '../books/kinkaku.epub'
    book = epub.read_epub(test_ebook)
    passed = 0
    failed = 0

    def check(name, condition, detail=''):
        global passed, failed
        if condition:
            print(f'  PASS: {name}')
            passed += 1
        else:
            print(f'  FAIL: {name} {detail}')
            failed += 1

    # ---- Test 1: Parse a range CFI string ----
    print('Test 1: Parse range CFI')
    parser = CFIParser()
    # Path: /6/12 = spine item 5 (0004.xhtml)
    # Redirect: !/4/2/12 = body -> div -> 6th child (p with "幼時から...")
    # Start: /1:1 = text node 0, offset 1  |  End: /3:8 = text node 1, offset 8
    cfi_str = 'epubcfi(/6/12!/4/2/12,/1:1,/3:8)'
    parsed = parser.parse_epubcfi(cfi_str)
    check('is_range', parsed['is_range'])
    check('parent has steps', len(parsed['parent'].get('steps', [])) >= 1)
    check('parent has redirect', 'redirect' in parsed['parent'])
    check('start has steps', len(parsed['start'].get('steps', [])) >= 1)
    check('end has steps', len(parsed['end'].get('steps', [])) >= 1)

    # ---- Test 2: Resolve range CFI to targets ----
    print('\nTest 2: Resolve range CFI')
    result = resolve_cfi(cfi_str, book)
    check('result is range', result is not None and result.get('type') == 'range')
    if result and result.get('type') == 'range':
        st = result['start'].get('target')
        et = result['end'].get('target')
        check('start target exists', st is not None)
        check('end target exists', et is not None)
        if st:
            check('start is text type', st.get('type') == 'text')
            check('start text_node_index=0', st.get('text_node_index') == 0,
                  f'got {st.get("text_node_index")}')
            check('start offset=1', st.get('offset') == 1, f'got {st.get("offset")}')
        if et:
            check('end is text type', et.get('type') == 'text')
            check('end text_node_index=1', et.get('text_node_index') == 1,
                  f'got {et.get("text_node_index")}')
            check('end offset=8', et.get('offset') == 8, f'got {et.get("offset")}')

    # ---- Test 3: Extract text from range ----
    print('\nTest 3: Extract text from range')
    expected_text = '幼時から父は、私によく、金閣のことを語った。'
    if result and result.get('type') == 'range':
        extracted = extract_range_text(result)
        print(extracted)
        check('extracted text is not None', extracted is not None)
        if extracted is not None:
            check('extracted text matches',
                  extracted == expected_text,
                  f'got {repr(extracted)} expected {repr(expected_text)}')
    else:
        check('range result available', False, 'no range result to extract from')

    # ---- Test 4: Generate CFI from text, then round-trip ----
    print('\nTest 4: Round-trip text -> CFI -> text')
    # Find the item for chapter 1
    target_text = '幼時から父は、私によく、金閣のことを語った。'
    # Use spine index 5 (0-based) which is /6/12 -> 0004.xhtml
    spine_entry = book.spine[5]
    item_id = _normalize_spine_entry(spine_entry)
    item = book.get_item_with_id(item_id)
    check('found item', item is not None, f'spine[5] id={item_id}')

    if item:
        generated_cfi = generate_range_cfi(book, item, target_text)
        check('generated CFI is not None', generated_cfi is not None)
        if generated_cfi:
            print(f'    generated: {generated_cfi}')
            # Now resolve it back
            rt_result = resolve_cfi(generated_cfi, book)
            check('round-trip resolves', rt_result is not None and rt_result.get('type') == 'range')
            if rt_result and rt_result.get('type') == 'range':
                rt_text = extract_range_text(rt_result)
                check('round-trip text matches',
                      rt_text == target_text,
                      f'got {repr(rt_text)} expected {repr(target_text)}')

    # ---- Test 5: More offset tests ----
    print('\nTest 5: Additional offset tests')
    # Test: first 3 chars of the "幼時から" paragraph (body/div/child[5] = /4/2/12)
    simple_cfi = 'epubcfi(/6/12!/4/2/12,/1:0,/1:3)'
    simple_result = resolve_cfi(simple_cfi, book)
    check('simple range resolves', simple_result is not None and simple_result.get('type') == 'range')
    if simple_result and simple_result.get('type') == 'range':
        simple_text = extract_range_text(simple_result)
        check('simple range extracts text', simple_text is not None)
        if simple_text:
            check('simple range text length=3', len(simple_text) == 3,
                  f'got len={len(simple_text)} text={repr(simple_text)}')
            print(f'    extracted: {repr(simple_text)}')

    # Next paragraph: body/div/child[6] = /4/2/14
    cfi2 = 'epubcfi(/6/12!/4/2/14,/1:0,/1:5)'
    r2 = resolve_cfi(cfi2, book)
    check('second paragraph resolves', r2 is not None and r2.get('type') == 'range')
    if r2 and r2.get('type') == 'range':
        t2 = extract_range_text(r2)
        check('second paragraph extracts text', t2 is not None)
        if t2:
            print(f'    para2 first 5 chars: {repr(t2)}')

    # ---- Summary ----
    print(f'\n=== {passed} passed, {failed} failed ===')
    if failed > 0:
        sys.exit(1)

    # ---- Test 6: Ruby annotation round-trip ----
    # <p>　しかし私は、...ほとんど<ruby>駈<rt>か</rt></ruby>けて行った。そこで...</p>
    # The "駈" is inside <ruby>, so readable text includes it but parent-level text doesn't.
    # This tests that generate_range_cfi searches readable text (with <rt> excluded)
    # and extract_range_text collects child element text between parent text nodes.
    print('\nTest 6: Ruby annotation round-trip')
    ruby_target = 'しかし私は、わざと少年らしく（私はこんな時だけ、故意の演技の場合だけ、少年らしかった）、陽気に先に立って、ほとんど駈けて行った。'
    generated_cfi2 = generate_range_cfi(book, item, ruby_target)
    check('generated CFI is not None', generated_cfi2 is not None)
    if generated_cfi2:
        print(f'    generated: {generated_cfi2}')
        rt_result2 = resolve_cfi(generated_cfi2, book)
        check('resolves to range', rt_result2 is not None and rt_result2.get('type') == 'range')
        if rt_result2 and rt_result2.get('type') == 'range':
            extracted2 = extract_range_text(rt_result2)
            check('extracted text matches',
                  extracted2 == ruby_target,
                  f'got {repr(extracted2)} expected {repr(ruby_target)}')

    # ---- Final Summary ----
    print(f'\n=== {passed} passed, {failed} failed ===')
    if failed > 0:
        sys.exit(1)
