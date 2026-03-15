"""Policy-driven XHTML extraction rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
import re


def _local_tag(tag) -> str:
    """Strip namespace from an lxml tag."""

    if isinstance(tag, str) and '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def _classes(element) -> set[str]:
    return set(element.get('class', '').split())


def _epub_types(element) -> set[str]:
    return set(element.get('{http://www.idpf.org/2007/ops}type', '').split())


class ExtractAction(Enum):
    """How the extractor should treat a node."""

    SKIP_ENTIRE = auto()
    KEEP_NORMAL = auto()
    KEEP_CHILDREN_ONLY = auto()
    KEEP_DIRECT_TEXT_ONLY = auto()
    INLINE_BREAK = auto()
    BLOCK_BREAK = auto()
    STRUCTURAL_CONTAINER = auto()


@dataclass(frozen=True)
class ElementPolicy:
    """A matching rule plus the extraction action for a node."""

    tag: str | None = None
    classes: frozenset[str] = frozenset()
    epub_type: str | None = None
    role: str | None = None
    id_pattern: str | None = None
    href_fragment_pattern: str | None = None
    action: ExtractAction = ExtractAction.KEEP_NORMAL
    name: str = ''

    def matches(self, element) -> bool:
        tag = _local_tag(element.tag)
        if not isinstance(tag, str):
            return False
        if self.tag is not None and tag != self.tag:
            return False
        if self.classes and not (_classes(element) & set(self.classes)):
            return False
        if self.epub_type is not None and self.epub_type not in _epub_types(element):
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


def _default_policies() -> list[ElementPolicy]:
    return [
        ElementPolicy(tag='rt', action=ExtractAction.SKIP_ENTIRE, name='skip-ruby-annotation'),
        ElementPolicy(tag='rp', action=ExtractAction.SKIP_ENTIRE, name='skip-ruby-parens'),
        ElementPolicy(tag='script', action=ExtractAction.SKIP_ENTIRE, name='skip-script'),
        ElementPolicy(tag='style', action=ExtractAction.SKIP_ENTIRE, name='skip-style'),
        ElementPolicy(tag='svg', action=ExtractAction.SKIP_ENTIRE, name='skip-svg'),
        ElementPolicy(tag='math', action=ExtractAction.SKIP_ENTIRE, name='skip-math'),
        ElementPolicy(tag='img', action=ExtractAction.SKIP_ENTIRE, name='skip-image'),
        ElementPolicy(tag='ruby', action=ExtractAction.KEEP_CHILDREN_ONLY, name='ruby-base-text'),
        ElementPolicy(tag='br', action=ExtractAction.INLINE_BREAK, name='inline-break'),
        ElementPolicy(tag='section', action=ExtractAction.STRUCTURAL_CONTAINER, name='section-container'),
        ElementPolicy(tag='article', action=ExtractAction.STRUCTURAL_CONTAINER, name='article-container'),
        ElementPolicy(tag='header', action=ExtractAction.STRUCTURAL_CONTAINER, name='header-container'),
        ElementPolicy(tag='footer', action=ExtractAction.STRUCTURAL_CONTAINER, name='footer-container'),
        ElementPolicy(tag='nav', epub_type='toc', action=ExtractAction.SKIP_ENTIRE, name='skip-toc-nav'),
        ElementPolicy(role='doc-toc', action=ExtractAction.SKIP_ENTIRE, name='skip-doc-toc'),
        ElementPolicy(tag='aside', epub_type='footnote', action=ExtractAction.SKIP_ENTIRE, name='skip-footnote-aside'),
        ElementPolicy(tag='a', classes=frozenset({'noteref', 'footnote-ref'}), action=ExtractAction.SKIP_ENTIRE, name='skip-noteref-class'),
        ElementPolicy(tag='a', epub_type='noteref', action=ExtractAction.SKIP_ENTIRE, name='skip-noteref-epub-type'),
        ElementPolicy(tag='span', classes=frozenset({'super'}), action=ExtractAction.SKIP_ENTIRE, name='skip-super'),
        ElementPolicy(classes=frozenset({'annotation'}), action=ExtractAction.SKIP_ENTIRE, name='skip-annotation-class'),
        ElementPolicy(classes=frozenset({'toc', 'toc-entry', 'pginternal'}), action=ExtractAction.SKIP_ENTIRE, name='skip-toc-class'),
        ElementPolicy(id_pattern=r'^(toc|nav|footnote)', action=ExtractAction.SKIP_ENTIRE, name='skip-known-id'),
        ElementPolicy(href_fragment_pattern=r'#(fn|footnote|note)', action=ExtractAction.SKIP_ENTIRE, name='skip-footnote-link'),
        ElementPolicy(tag='p', action=ExtractAction.BLOCK_BREAK, name='paragraph'),
        ElementPolicy(tag='div', action=ExtractAction.BLOCK_BREAK, name='div-block'),
        ElementPolicy(tag='blockquote', action=ExtractAction.BLOCK_BREAK, name='blockquote'),
        ElementPolicy(tag='li', action=ExtractAction.BLOCK_BREAK, name='list-item'),
        ElementPolicy(tag='dt', action=ExtractAction.BLOCK_BREAK, name='definition-term'),
        ElementPolicy(tag='dd', action=ExtractAction.BLOCK_BREAK, name='definition-detail'),
        ElementPolicy(tag='figcaption', action=ExtractAction.BLOCK_BREAK, name='figcaption'),
        ElementPolicy(tag='pre', action=ExtractAction.BLOCK_BREAK, name='preformatted'),
        ElementPolicy(tag='h1', action=ExtractAction.BLOCK_BREAK, name='heading-1'),
        ElementPolicy(tag='h2', action=ExtractAction.BLOCK_BREAK, name='heading-2'),
        ElementPolicy(tag='h3', action=ExtractAction.BLOCK_BREAK, name='heading-3'),
        ElementPolicy(tag='h4', action=ExtractAction.BLOCK_BREAK, name='heading-4'),
        ElementPolicy(tag='h5', action=ExtractAction.BLOCK_BREAK, name='heading-5'),
        ElementPolicy(tag='h6', action=ExtractAction.BLOCK_BREAK, name='heading-6'),
        ElementPolicy(tag='strong', action=ExtractAction.KEEP_NORMAL, name='keep-strong'),
        ElementPolicy(tag='em', action=ExtractAction.KEEP_NORMAL, name='keep-em'),
        ElementPolicy(tag='b', action=ExtractAction.KEEP_NORMAL, name='keep-bold'),
        ElementPolicy(tag='i', action=ExtractAction.KEEP_NORMAL, name='keep-italic'),
    ]


@dataclass
class TagFilterConfig:
    """Policy configuration for XHTML text extraction."""

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
    skip_rules: list[ElementPolicy] = field(default_factory=lambda: [
        ElementPolicy(tag='a', classes=frozenset({'noteref', 'footnote-ref'})),
        ElementPolicy(tag='a', epub_type='noteref'),
        ElementPolicy(tag='aside', epub_type='footnote'),
        ElementPolicy(tag='nav', epub_type='toc'),
        ElementPolicy(role='doc-toc'),
        ElementPolicy(id_pattern=r'^(toc|nav|footnote)'),
        ElementPolicy(href_fragment_pattern=r'#(fn|footnote|note)'),
    ])
    policies: list[ElementPolicy] = field(default_factory=_default_policies)
    default_action: ExtractAction = ExtractAction.KEEP_NORMAL
    inline_break_text: str = ' '
    structural_tags: set[str] = field(default_factory=lambda: {
        'section', 'article', 'header', 'footer', 'nav',
    })
    apply_segment_heuristics: bool = True
    drop_numeric_break_markers: bool = True
    skip_text_patterns: list[str] = field(default_factory=lambda: [
        r'project gutenberg',
        r'get gutindex',
        r'trademark license fee',
        r'all rights reserved',
        r'\betexts?\b',
        r'small print',
        r'disclaims most of our liability',
        r'table of contents',
        r'\bcontents\b',
        r'isbn',
        r'copyright',
        r'www\.gutenberg',
        r'mobipocket reader',
        r'generated by calibre',
    ])
    skip_heading_patterns: list[str] = field(default_factory=lambda: [
        r'^(chapter|book|part|contents?)\b',
        r'^(cap[ií]tulo|parte|contenido)\b',
        r'^第\s*[一二三四五六七八九十百千0-9]+\s*[章节回部篇卷]$',
    ])
    skip_line_patterns: list[str] = field(default_factory=lambda: [
        r'^[0-9]{1,4}(?:/[0-9]{1,4}){0,2}$',
        r'^＊[一二三四五六七八九十百千〇零0-9]+$',
        r'^[×\*\-_=~·•\.\s]{3,}$',
    ])

    def __post_init__(self) -> None:
        legacy_policies: list[ElementPolicy] = []

        covered_skip_tags = {policy.tag for policy in self.policies if policy.action == ExtractAction.SKIP_ENTIRE}
        for tag in sorted(self.skip_tags - {tag for tag in covered_skip_tags if tag}):
            legacy_policies.append(
                ElementPolicy(tag=tag, action=ExtractAction.SKIP_ENTIRE, name=f'legacy-skip-tag:{tag}')
            )

        for classes in sorted(self.skip_classes):
            legacy_policies.append(
                ElementPolicy(classes=frozenset({classes}), action=ExtractAction.SKIP_ENTIRE, name=f'legacy-skip-class:{classes}')
            )

        for rule in self.skip_rules:
            legacy_policies.append(
                ElementPolicy(
                    tag=rule.tag,
                    classes=rule.classes,
                    epub_type=rule.epub_type,
                    role=rule.role,
                    id_pattern=rule.id_pattern,
                    href_fragment_pattern=rule.href_fragment_pattern,
                    action=ExtractAction.SKIP_ENTIRE,
                    name=rule.name or 'legacy-skip-rule',
                )
            )

        covered_block_tags = {policy.tag for policy in self.policies if policy.action == ExtractAction.BLOCK_BREAK}
        covered_structural_tags = {policy.tag for policy in self.policies if policy.action == ExtractAction.STRUCTURAL_CONTAINER}
        for tag in sorted(self.block_tags):
            if tag in covered_block_tags or tag in covered_structural_tags:
                continue
            action = ExtractAction.STRUCTURAL_CONTAINER if tag in self.structural_tags else ExtractAction.BLOCK_BREAK
            legacy_policies.append(
                ElementPolicy(tag=tag, action=action, name=f'legacy-block-tag:{tag}')
            )

        for tag in sorted(self.include_child_text_tags):
            if any(policy.tag == tag for policy in self.policies):
                continue
            legacy_policies.append(
                ElementPolicy(tag=tag, action=ExtractAction.KEEP_CHILDREN_ONLY, name=f'legacy-child-text:{tag}')
            )

        self.policies.extend(legacy_policies)


def match_element_policy(element, config: TagFilterConfig) -> ElementPolicy | None:
    """Return the first matching policy for *element*."""

    tag = _local_tag(element.tag)
    if not isinstance(tag, str):
        return None
    for policy in config.policies:
        if policy.matches(element):
            return policy
    return None


def get_extract_action(element, config: TagFilterConfig) -> ExtractAction:
    """Return the effective action for *element*."""

    policy = match_element_policy(element, config)
    if policy is None:
        return config.default_action
    return policy.action


def should_skip_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* should be skipped during extraction."""

    return get_extract_action(element, config) == ExtractAction.SKIP_ENTIRE


def is_block_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* behaves as a block-level extraction node."""

    return get_extract_action(element, config) in {
        ExtractAction.BLOCK_BREAK,
        ExtractAction.STRUCTURAL_CONTAINER,
    }


def is_structural_container(element, config: TagFilterConfig) -> bool:
    """Heuristically detect wrapper nodes that should not become segments."""

    if get_extract_action(element, config) == ExtractAction.STRUCTURAL_CONTAINER:
        return True
    if not is_block_element(element, config):
        return False

    tag = _local_tag(element.tag)
    child_blocks = [
        child for child in element
        if isinstance(child.tag, str)
        and is_block_element(child, config)
        and not should_skip_element(child, config)
    ]
    if tag == 'div' and len(child_blocks) >= 2 and not (element.text or '').strip():
        return True
    return False
