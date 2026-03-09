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


def cfi_to_xpath(cfi_dict):
    """
    convert cfi redirect steps to an xpath expression
    now support only offset assertion without parameters
    epubcfi(/6/4!/2/1:3) -> /child::6/child::4/child::2/child::1[position()=3]
    """
    from lxml.etree import XPathEvalError
    if not cfi_dict.get('redirect'):
        return None
    redirect_steps = cfi_dict['redirect']['step']
    xpath = ''
    for step in redirect_steps:
        if 'offset' not in step:
            if 'id' in step:
                xpath += f'descendant::{step["id"]}[{step["num"]}]'
            else:
                xpath += f'child::{step["num"]}'
        else:
            # locate offset in xpath
            pass
    return xpath

def cfi_to_content(cfi_dict, book: epub.EpubHtml):
    xpath = 

def xpath_to_element(xpath, xhtml: epub.EpubHtml):
    content = xhtml.get_content().decode('utf-8')
    from lxml import html
    tree = html.fromstring(content)
    tree.ma
    pass

def xpath_to_cfi(xpath):
    pass

def cfi_to_item(cfi_dict, book: epub.EpubBook):
    """
    """
    steps = cfi_dict.get('steps', [])
    if not steps:
        return None
    item_index = [step['num'] / 2 - 1 for step in steps]
    manifest_list = list(book.get_items())
    spine_list = [item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)]
    if item_index[0] == 1:
        return manifest_list[item_index[1]]
    elif item_index[0] == 2:
        return spine_list[item_index[1]]
    elif item_index[0] == 0:
        return None
    # matadata_item_index = item_index[0] - 3

if __name__ == '__main__':
    test_ebook = "../books/her.epub"
    book = epub.read_epub(test_ebook)
    ebook_reader = epub.EpubReader(test_ebook)
    book = ebook_reader.load()
    print([item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)])
    # print(ebook_reader.opf_file)
    # print(list(book.get_items()))
    # print(book.metadata)
    for item in book.get_items():
        print(item.get_name(), item.get_type(), item.get_id())
    print(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))[3].manifest)
    print(type(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))[3]))