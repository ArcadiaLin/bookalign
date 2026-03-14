"""XHTML 标签过滤规则定义。"""

from dataclasses import dataclass, field


@dataclass
class TagFilterConfig:
    """Configuration for filtering XHTML elements during text extraction.

    - ``skip_tags``: elements whose **entire subtree** is skipped
      (e.g. ``<rt>``, ``<rp>`` ruby annotations, ``<script>``, ``<style>``).
    - ``skip_classes``: elements with any of these CSS classes are skipped
      (e.g. footnote markers like ``<span class="super">``).
    - ``block_tags``: block-level elements that form paragraph boundaries.
    """

    skip_tags: set[str] = field(default_factory=lambda: {
        'rt', 'rp', 'script', 'style',
    })
    skip_classes: set[str] = field(default_factory=lambda: {
        'super', 'noteref', 'footnote-ref', 'annotation',
    })
    block_tags: set[str] = field(default_factory=lambda: {
        'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'li', 'dt', 'dd', 'section', 'article',
        'header', 'footer', 'figcaption', 'pre',
    })


def _local_tag(tag) -> str:
    """Strip namespace: ``'{ns}name'`` -> ``'name'``."""
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}')[1]
    return tag


def should_skip_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* should be entirely skipped during extraction.

    An element is skipped if:
    - Its tag (without namespace) is in ``config.skip_tags``
    - Any of its CSS classes are in ``config.skip_classes``

    Note: ``<ruby>`` is **not** skipped — only its ``<rt>``/``<rp>`` children are.
    """
    tag = _local_tag(element.tag)
    if not isinstance(tag, str):
        return True

    if tag in config.skip_tags:
        return True

    classes = set(element.get('class', '').split())
    if classes & config.skip_classes:
        return True

    return False


def is_block_element(element, config: TagFilterConfig) -> bool:
    """Return True if *element* is a block-level element."""
    tag = _local_tag(element.tag)
    if not isinstance(tag, str):
        return False
    return tag in config.block_tags
