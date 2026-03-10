import re
from dataclasses import dataclass
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
        """
        return:
        {
            'parent': {...} | {},
            'start': {...} | {},
            'end': {...} | {},
            'is_range': bool,
            'raw_tail': str,
        }
        """
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
        """
        这里只处理 before / after，不处理 params。
        """
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

        # 暂不处理 params
        if not raw.startswith(']'):
            return original_raw

        if ta:
            ans['assertion'] = ta
        return raw[1:]


# =========================== Package-level ===========================

def _normalize_spine_entry(entry):
    """
    按你当前脚本的使用方式，只保留严格耦合的几种 spine entry 形式。
    """
    if isinstance(entry, tuple):
        return entry[0]
    if isinstance(entry, str):
        return entry
    if hasattr(entry, "id"):
        return entry.id
    if hasattr(entry, "get_id"):
        return entry.get_id()
    return None


def _step_to_zero_based_even_index(num: int) -> Optional[int]:
    """
    /2 -> 0
    /4 -> 1
    /6 -> 2
    """
    if not isinstance(num, int) or num < 2 or num % 2 != 0:
        return None
    return num // 2 - 1


def package_steps_to_item(cfi_dict: Dict[str, Any], book: epub.EpubBook) -> Optional[epub.EpubItem]:
    """
    只支持 package -> spine -> itemref 这条路径。
    即：
        /6 -> spine
        /6/2 -> spine 第1个 itemref
        /6/4 -> spine 第2个 itemref
    """
    steps = cfi_dict.get('steps', [])
    if len(steps) < 2:
        return None

    first_num = steps[0].get('num')
    second_num = steps[1].get('num')

    first_idx = _step_to_zero_based_even_index(first_num)
    second_idx = _step_to_zero_based_even_index(second_num)

    # package children:
    # /2 -> metadata
    # /4 -> manifest
    # /6 -> spine
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


def get_item_root(item: epub.EpubItem):
    """
    将 EpubItem 内容解析为 lxml root
    """
    content = item.get_content()
    parser = etree.XMLParser(recover=True)
    return etree.fromstring(content, parser=parser)


# =========================== Document-level ===========================

def _element_children(node) -> List[Any]:
    return [child for child in node if isinstance(child.tag, str)]


def _resolve_even_step(node, num: int):
    idx = _step_to_zero_based_even_index(num)
    if idx is None:
        return None
    children = _element_children(node)
    if idx >= len(children):
        return None
    return children[idx]


def _collect_all_text(node) -> str:
    return ''.join(node.itertext())


def _check_text_assertion(node, assertion: Optional[Dict[str, Any]]) -> bool:
    """
    简化实现：
    - before: 目标位置前方文本片段应包含 before
    - after: 目标位置后方文本片段应包含 after

    在当前实现里，assertion 只在 offset 已经解析出来后再校验更合理。
    这里对元素节点本身只做宽松检查：其文本内容中应包含 before/after 至少一方。
    """
    if not assertion:
        return True

    text = _collect_all_text(node)
    before = assertion.get('before')
    after = assertion.get('after')

    if before and before not in text:
        return False
    if after and after not in text:
        return False
    return True


def resolve_redirect_steps(root, redirect: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    直接步进 document DOM。
    当前策略：
    - 偶数 step: 走 element child
    - 偶数 step 带 id: 严格要求 child 上 id 匹配
    - 奇数 step: 仅允许最后一步，用于 terminal offset
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
            next_node = _resolve_even_step(node, num)
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
            if i == len(steps) - 1:
                return {
                    'node': node,
                    'offset': step.get('offset', 0),
                    'assertion': step.get('assertion'),
                    'terminal_step': step,
                }
            return None

        return None

    last_step = steps[-1]
    return {
        'node': node,
        'offset': last_step.get('offset', 0),
        'assertion': last_step.get('assertion'),
        'terminal_step': last_step,
    }


# =========================== Offset / Assertion ===========================

def iter_text_segments(element) -> Iterator[Tuple[Any, str, str]]:
    """
    顺序产出直接文本段：
    - element.text
    - child.tail
    """
    if element.text:
        yield (element, 'text', element.text)

    for child in element:
        if child.tail:
            yield (child, 'tail', child.tail)


def resolve_text_offset(resolved: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not resolved:
        return None

    node = resolved['node']
    offset = resolved.get('offset')
    assertion = resolved.get('assertion')

    if offset is None:
        if assertion and not _check_text_assertion(node, assertion):
            return None
        return {
            'type': 'element',
            'node': node,
            'assertion': assertion,
        }

    if offset < 0:
        return None

    remain = offset
    collected_before = ''
    segments = list(iter_text_segments(node))

    for owner, kind, text in segments:
        if remain <= len(text):
            before_text = collected_before + text[:remain]
            after_text = text[remain:] + ''.join(seg[2] for seg in segments[segments.index((owner, kind, text)) + 1:])

            if assertion:
                before = assertion.get('before')
                after = assertion.get('after')
                if before is not None and not before_text.endswith(before):
                    return None
                if after is not None and not after_text.startswith(after):
                    return None

            return {
                'type': 'text',
                'node': owner,
                'kind': kind,
                'text': text,
                'offset': remain,
                'assertion': assertion,
            }

        collected_before += text
        remain -= len(text)

    if remain == 0:
        text = node.text or ''
        if assertion:
            before = assertion.get('before')
            after = assertion.get('after')
            if before is not None and not text.endswith(before):
                return None
            if after is not None and after != '':
                return None

        return {
            'type': 'text',
            'node': node,
            'kind': 'text',
            'text': text,
            'offset': len(text),
            'assertion': assertion,
        }

    return None


# =========================== Single CFI Resolution ===========================

def resolve_path_to_target(path_cfi: Dict[str, Any], book: epub.EpubBook) -> Optional[Dict[str, Any]]:
    """
    解析单一路径 CFI（不是 range）
    """
    epub_item = package_steps_to_item(path_cfi, book)
    if epub_item is None:
        return None

    root = get_item_root(epub_item)
    redirect = path_cfi.get('redirect')

    if not redirect:
        return {
            'item': epub_item,
            'target': None,
        }

    redirect_resolved = resolve_redirect_steps(root, redirect)
    if redirect_resolved is None:
        return {
            'item': epub_item,
            'target': None,
        }

    target = resolve_text_offset(redirect_resolved)
    return {
        'item': epub_item,
        'target': target,
    }


# =========================== Range CFI ===========================

def resolve_cfi_to_target(cfi_str: str, book: epub.EpubBook) -> Optional[Dict[str, Any]]:
    """
    支持：
    - 普通 CFI
    - range CFI: epubcfi(parent,start,end)
    """
    parsed = CFIParser().parse_epubcfi(cfi_str)
    parent = parsed.get('parent')
    if not parent:
        return None

    if not parsed.get('is_range'):
        return resolve_path_to_target(parent, book)

    start = parsed.get('start')
    end = parsed.get('end')
    if not start or not end:
        return None

    # range CFI 语义：start / end 是相对于 parent 的补充路径
    start_path = _merge_range_path(parent, start)
    end_path = _merge_range_path(parent, end)

    start_target = resolve_path_to_target(start_path, book)
    end_target = resolve_path_to_target(end_path, book)

    if start_target is None or end_target is None:
        return None

    return {
        'type': 'range',
        'start': start_target,
        'end': end_target,
    }


def _merge_range_path(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 range 的 parent path 和 start/end path 合并成完整 path
    """
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


# =========================== Debug / Example ===========================

if __name__ == '__main__':
    test_ebook = '../books/kinkaku.epub'
    book = epub.read_epub(test_ebook)

    cfi = 'epubcfi(/6/12!/4/16,/1:5,/1:10)'
    result = resolve_cfi_to_target(cfi, book)
    # print(result['item'].get_id())
    print(result)