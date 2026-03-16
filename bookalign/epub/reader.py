"""EPUB 读取：EPUB -> 章节文档列表 + 元数据。"""

from pathlib import Path

import ebooklib
from ebooklib import epub


def read_epub(path: str | Path) -> epub.EpubBook:
    """Read an EPUB file and return an EpubBook object."""
    return epub.read_epub(str(path))


def get_spine_documents(book: epub.EpubBook) -> list[tuple[int, epub.EpubHtml]]:
    """Return spine documents in order as ``(spine_index, EpubHtml)`` pairs.

    Skips non-XHTML items (images, CSS, etc.).
    """
    results: list[tuple[int, epub.EpubHtml]] = []
    for i, entry in enumerate(book.spine):
        item = None
        if isinstance(entry, tuple):
            item = book.get_item_with_id(entry[0])
        elif hasattr(entry, 'get_type'):
            item = entry
        else:
            item = book.get_item_with_id(entry)
        if (
            item is not None
            and item.get_type() == ebooklib.ITEM_DOCUMENT
            and not isinstance(item, epub.EpubNav)
        ):
            results.append((i, item))
    return results


def get_metadata(book: epub.EpubBook) -> dict:
    """Extract basic metadata from an EPUB book.

    Returns dict with keys: ``title``, ``author``, ``language``.
    """
    def _first(items):
        if items:
            val = items[0]
            return val[0] if isinstance(val, tuple) else val
        return ''

    title = _first(book.get_metadata('DC', 'title'))
    creator = _first(book.get_metadata('DC', 'creator'))
    language = _first(book.get_metadata('DC', 'language'))

    return {
        'title': title or '',
        'author': creator or '',
        'language': language or '',
    }
