"""Configurable XHTML filtering rules for text extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
import re


def _local_tag(tag) -> str:
    """Strip namespace from an lxml tag."""

    if isinstance(tag, str) and '}' in tag:
        return tag.split('}', 1)[1]
    return tag


@dataclass(frozen=True)
class ElementRule:
    """Rule used to ignore structural or annotation nodes."""

    tag: str | None = None
    classes: frozenset[str] = frozenset()
    epub_type: str | None = None
    role: str | None = None
    id_pattern: str | None = None
    href_fragment_pattern: str | None = None

    def matches(self, element) -> bool:
        tag = _local_tag(element.tag)
        if not isinstance(tag, str):
            return False
        if self.tag is not None and tag != self.tag:
            return False
        if self.classes:
            classes = set(element.get('class', '').split())
            if not (classes & set(self.classes)):
                return False
        if self.epub_type is not None:
            epub_type = element.get('{http://www.idpf.org/2007/ops}type', '')
            if self.epub_type not in epub_type.split():
                return False
        if self.role is not None and element.get('role') != self.role:
            return False
        if self.id_pattern is not None:
            element_id = element.get('id', '')
            if not re.search(self.id_pattern, element_id, re.IGNORECASE):
                return False
        if self.href_fragment_pattern is not None:
            href = element.get('href', '')
            if not re.search(self.href_fragment_pattern, href, re.IGNORECASE):
                return False
        return True


@dataclass
class TagFilterConfig:
    """Configuration for filtering XHTML elements during text extraction."""

    skip_tags: set[str] = field(default_factory=lambda: {
        'rt', 'rp', 'script', 'style', 'svg', 'math', 'img',
    })
    skip_classes: set[str] = field(default_factory=lambda: {
        'super', 'noteref', 'footnote-ref', 'annotation',
        'toc', 'toc-entry', 'pginternal',
    })
    block_tags: set[str] = field(default_factory=lambda: {
        'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'li', 'dt', 'dd', 'section', 'article',
        'header', 'footer', 'figcaption', 'pre',
    })
    include_child_text_tags: set[str] = field(default_factory=lambda: {'ruby'})
    skip_rules: list[ElementRule] = field(default_factory=lambda: [
        ElementRule(tag='a', classes=frozenset({'noteref', 'footnote-ref'})),
        ElementRule(tag='a', epub_type='noteref'),
        ElementRule(tag='aside', epub_type='footnote'),
        ElementRule(tag='nav', epub_type='toc'),
        ElementRule(role='doc-toc'),
        ElementRule(id_pattern=r'^(toc|nav|footnote)'),
        ElementRule(href_fragment_pattern=r'#(fn|footnote|note)'),
    ])


def should_skip_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* should be skipped during extraction."""

    tag = _local_tag(element.tag)
    if not isinstance(tag, str):
        return True

    if tag in config.skip_tags:
        return True

    classes = set(element.get('class', '').split())
    if classes & config.skip_classes:
        return True

    return any(rule.matches(element) for rule in config.skip_rules)


def is_block_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* is a block-level element."""

    tag = _local_tag(element.tag)
    return isinstance(tag, str) and tag in config.block_tags


def is_structural_container(element, config: TagFilterConfig) -> bool:
    """Heuristically detect wrapper nodes that should not become segments."""

    if not is_block_element(element, config):
        return False

    tag = _local_tag(element.tag)
    child_blocks = [
        child for child in element
        if isinstance(child.tag, str)
        and is_block_element(child, config)
        and not should_skip_element(child, config)
    ]
    if tag in {'section', 'article', 'header', 'footer', 'nav'} and child_blocks:
        return True
    if tag == 'div' and len(child_blocks) >= 2:
        direct_text = (element.text or '').strip()
        if not direct_text:
            return True
    return False
