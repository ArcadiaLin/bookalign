import re

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
    
def decode_cfi(cfi_str):
    parser = CFIParser()
    return parser.parse_epubcfi(cfi_str)

def encode_cfi(cfi_dict):
    # TODO
    pass