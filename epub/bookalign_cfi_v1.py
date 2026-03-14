import re
from ebooklib import epub
import ebooklib
from lxml.etree import XPathEvalError

class CFIParser:
    def __init__(self):
        # All allowed unicode characters + escaped special characters
        special_char = r'[\[\](),;=^]'
        unescaped_char = (
            rf'(?:(?!{special_char})'
            r'[\t\n\r -\ud7ff\ue000-\ufffd\U00010000-\U0010ffff])'
        )
        # not strictly spec compliant
        escaped_char = r'\^' + special_char[:-1] + '-]'
        chars = fr'(?:{unescaped_char}|(?:{escaped_char}))+'
        chars_no_space = chars.replace('0020', '0021')
        # No leading zeros allowed for integers
        integer = r'(?:[1-9][0-9]*)|0'
        # No leading zeros, except for numbers in (0, 1) and no trailing zeros for the fractional part
        def c(x):
            return re.compile(x)

        # A step of the form /integer
        self.step_pat = c(rf'/({integer})')
        # An id assertion of the form [characters]
        self.id_assertion_pat = c(rf'\[({chars})\]')

        # A text offset of the form :integer
        self.offset_pat = c(rf':({integer})')

        # assertion patterns
        self.ta1_pat = c(rf'({chars})(?:,({chars})){{0,1}}')
        self.ta2_pat = c(rf',({chars})')
        # single parameter pattern
        self.parameter_pat = c(fr';({chars_no_space})=((?:{chars})(?:,(?:{chars}))*)')
        # single csv item pattern
        self.csv_item_pat = c(rf'({chars})(?:,|$)')

        # Unescape characters
        unescape_pat = c(fr'{escaped_char[:2]}({escaped_char[2:]})')
        self.unescape = lambda x: unescape_pat.sub(r'\1', x)
        
    def parse_epubcfi(self, raw):
        null = {}, {}, {}, raw
        if not raw:
            return null
        
        if not raw.startswith('epubcfi(') or not raw.endswith(')'):
            return null
        
        # remove the leading 'epubcfi(' and the trailing ')'
        raw = raw[len("epubcfi("): -1]
        parent_cfi, raw = self.parse_path(raw)
        if not parent_cfi:
            return null
        start_cfi, end_cfi = {}, {}
        if raw.startswith(','):
            start_cfi, raw = self.parse_path(raw[1:])
            if raw.startswith(','):
                end_cfi, raw = self.parse_path(raw[1:])
            if not start_cfi or not end_cfi:
                return null
        
        return parent_cfi, start_cfi, end_cfi, raw
    
    def do_match(self, pat, raw):
        m = pat.match(raw)
        if m is not None:
            raw = raw[m.end():]
        return m, raw

    def parse_path(self, raw):
        ' Parse a path of the form path [ , path ] '
        path = {'steps':[]}
        raw  = self._parse_path(raw, path)
        if not path['steps']:
            path = {}
        return path, raw
        
    def _parse_path(self, raw, ans):
        """
        raw = "/6/4[chap01ref]!/4[body01]/10[para05]/2/1:3"
        return like this:
{
    'steps': [
        {'num': 6},
        {'num': 4, 'id': 'chap01ref'}
    ],
    'redirect': {
        'steps': [
            {'num': 4, 'id': 'body01'},
            {'num': 10, 'id': 'para05'},
            {'num': 2},
            {'num': 1, 'offset': 3}
        ]
    }
}
        """
        m, raw = self.do_match(self.step_pat, raw)
        if m is None:
            return raw
        ans['steps'].append({'num':int(m.group(1))})
        m, raw = self.do_match(self.id_assertion_pat, raw)
        if m is not None:
            ans['steps'][-1]['id'] = self.unescape(m.group(1))
        if raw.startswith('!'):
            ans['redirect'] = r = {'steps':[]}
            return self._parse_path(raw[1:], r)
        else:
            remaining_raw = self.parse_offset(raw, ans['steps'][-1])
            return self._parse_path(raw, ans) if remaining_raw is None else remaining_raw
    
    def parse_offset(self, raw, ans):
        m, raw = self.do_match(self.offset_pat, raw)
        if m is not None:
            ans["offset"] = int(m.group(1))
            return self.parse_assertion(raw, ans)
        
    def parse_assertion(self, raw, ans):
        """
epubcfi(/6/4!/2/1:3[before,after;s=b]) parsed like
{
    'steps': [
        {'num': 6},
        {'num': 4}
    ],
    'redirect': {
        'steps': [
            {'num': 2},
            {
                'num': 1,
                'offset': 3,
                'assertion': {
                    'before': 'before',
                    'after': 'after',
                    'params': {
                        's': ('b',)
                    }
                }
            }
        ]
    }
}
        """
        oraw = raw
        if not raw.startswith('['):
            return oraw

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
        
        params, raw = self.parse_parameters(raw)
        if params:
            ta['params'] = params

        if not raw.startswith(']'):
            return oraw

        if ta:
            ans['assertion'] = ta
        return raw[1:]
        
    def parse_csv(self, raw):
        values = []
        while True:
            m, new_raw = self.do_match(self.csv_item_pat, raw)
            if m is None:
                break
            values.append(self.unescape(m.group(1)))
            raw = new_raw
        return tuple(values)

    def parse_parameters(self, raw):
        params = {}
        while True:
            m, new_raw = self.do_match(self.parameter_pat, raw)
            if m is None:
                break
            name = self.unescape(m.group(1))
            value = m.group(2)
            params[name] = self.parse_csv(value)
            raw = new_raw
        return params, raw

# 从steps找到epubItem
def _normalize_spine_entry(entry):
    """
    EbookLib 的 spine 项可能是：
    - 'nav'
    - ('chapter_1', 'yes')
    - item object
    这里统一提取出 idref / uid
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

def package_steps_to_item(cfi_dict, book: epub.EpubBook) -> epub.EpubItem:
    steps = cfi_dict.get('steps', [])
    if len(steps) < 2:
        return None
    item_idx = [step['num'] / 2 - 1 for step in steps]

    manifest_items = list(book.get_items())
    spine_items = [book.get_item_with_id(_normalize_spine_entry(item)) for item in book.spine]
    if item_idx[0] == 1:
        return manifest_items[item_idx[1]]
    elif item_idx[0] == 2:
        return spine_items[item_idx[1]]
    elif item_idx[0] == 0:
        return None

# =========================== 处理 redirect steps ===========================
def _element_children(node):
    return [child for child in node if isinstance(child.tag, str)]

def _resolve_even_step(node, num):
    """
    偶数 step 表示第几个 element child。
    /2 -> 第1个元素子节点
    /4 -> 第2个元素子节点
    """
    if num % 2 != 0:
        return None
    if idx := num // 2 - 1 < 0 or idx >= len(_element_children(node)): 
        return None
    return _element_children(node)[idx]

def resolve_redirect_steps(node, redirect):
    if not redirect:
        return None
    for i, step in enumerate(redirect['steps']):
        num = step.get('num')
        node_id = step.get('id')
        
        if isinstance(num, int) and num % 2 == 0:
            next_node = _resolve_even_step(node, num)
            if next_node is None:
                return None
            if node_id is not None:
                actual_id = next_node.get("id")
                if actual_id != node_id:
                    raise ValueError(f"ID assertion failed at step {i}: expected {node_id}, got {actual_id}")
            node = next_node
            continue
        
        if isinstance(num, int) and num % 2 == 1:
            if i == len(redirect['steps']) - 1:
                return {
                    "node": node,
                    "offset": step.get("offset", 0),
                    "assertion": step.get("assertion"),
                    "terminal_step": step,
                }
        return None

    last_step = redirect['steps'][-1] if redirect['steps'] else None
    return {
        "node": node,
        "offset": last_step.get("offset", 0) if last_step else 0,
        "assertion": last_step.get("assertion") if last_step else None,
        "terminal_step": last_step,
    }

def iter_text_segments(element):
    if element.text:
        yield (element, 'text', element.text)
    
    for child in element:
        if child.tail:
            yield (child, 'tail', child.tail)

def resolve_text_offset(resolved):
    if not resolved:
        return None
    
    node = resolved['node']
    offset = resolved['offset']
    if offset is None:
        return {
            "type": "element",
            "node": node,
        }
    
    remain = offset
    for owner, kind, text in iter_text_segments(node):
        if remain <= len(text):
            return {
                "type": "text",
                "node": owner,
                "kind": kind,
                "text": text,
                "offset": remain,
            }
        remain -= len(text)
    
    if remain == 0:
        return {
            "type": "text",
            "node": node,
            "kind": "text",
            "text": node.text or "",
            "offset": len(node.text or ""),
        }
    return None


def resolve_cfi_to_target(cfi_str, book: epub.EpubBook):
    cfi_dict = CFIParser().parse_epubcfi(cfi_str)
    epub_item = package_steps_to_item(cfi_dict, book)
    if epub_item is None:
        return None
    root = epub_item.content
    
    redirect_resolved = resolve_redirect_steps(root, cfi_dict.get("redirect"))
    if redirect_resolved is None:
        return {
            "item": epub_item,
            "target": None,
        }
    
    target = resolve_text_offset(redirect_resolved)
    return {
        "item": epub_item,
        "target": target,
    }

if __name__ == '__main__':
    test_ebook = "../books/her.epub"
    book = epub.read_epub(test_ebook)
    ebook_reader = epub.EpubReader(test_ebook)
    book = ebook_reader.load()
    print(book.spine)
    print([item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)])
    # print(ebook_reader.opf_file)
    # print(list(book.get_items()))
    # print(book.metadata)
    for item in book.get_items():
        print(item.get_name(), item.get_type(), item.get_id())
    print(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))[3].manifest)
    print(type(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))[3]))