"""双语 EPUB 重建与输出。

将对齐结果注入到原书结构中，生成双语对照 EPUB。
"""

from __future__ import annotations

import copy
from pathlib import Path

import ebooklib
from ebooklib import epub
from lxml import etree

from bookalign.models.types import AlignmentResult, AlignedPair, Segment
from bookalign.epub.cfi import (
    CFIParser,
    resolve_spine_item,
    parse_item_xml,
    _merge_paths,
    resolve_dom_steps,
    _normalize_spine_entry,
)
from bookalign.epub.reader import get_spine_documents


# ═══════════════════════════════ CSS styles ═══════════════════════════════════

_BILINGUAL_CSS = """\
.bilingual-pair {
  margin: 1em 0;
}
.bilingual-pair .source {
  margin-bottom: 0.3em;
}
.bilingual-pair .translation {
  color: #555;
  font-size: 0.95em;
  margin-top: 0;
  padding-left: 0.5em;
  border-left: 2px solid #ccc;
}
.sentence-pair {
  margin: 0.5em 0;
}
.sentence-pair .src-sent {
  margin: 0 0 0.1em 0;
}
.sentence-pair .tgt-sent {
  color: #555;
  font-size: 0.93em;
  margin: 0 0 0.3em 0.5em;
}
"""


# ═══════════════════════════════ Main builder ═════════════════════════════════

def build_bilingual_epub(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
) -> None:
    """Build a bilingual EPUB from alignment results.

    Strategy:
    1. Copy the source book structure (metadata, CSS, images, TOC).
    2. Inject bilingual CSS.
    3. For each aligned chapter, insert translation after source paragraphs.
    4. Write the result to *output_path*.
    """
    out_book = epub.EpubBook()

    # Copy metadata
    _copy_metadata(source_book, out_book)

    # Add bilingual CSS
    css_item = epub.EpubItem(
        uid='bilingual-css',
        file_name='style/bilingual.css',
        media_type='text/css',
        content=_BILINGUAL_CSS.encode('utf-8'),
    )
    out_book.add_item(css_item)

    # Copy non-document items (CSS, images, fonts)
    for item in source_book.get_items():
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            out_book.add_item(item)

    # Group alignment pairs by chapter
    pairs_by_chapter: dict[int, list[AlignedPair]] = {}
    for pair in alignment.pairs:
        if pair.source:
            ch_idx = pair.source[0].chapter_idx
            pairs_by_chapter.setdefault(ch_idx, []).append(pair)

    # Process each spine document
    spine_docs = get_spine_documents(source_book)
    new_spine: list[tuple[str, str]] = []

    for spine_idx, doc in spine_docs:
        chapter_pairs = pairs_by_chapter.get(spine_idx, [])

        if chapter_pairs:
            new_content = _inject_translations(
                doc, chapter_pairs, alignment.granularity
            )
        else:
            new_content = doc.get_content()

        new_item = epub.EpubHtml(
            title=getattr(doc, 'title', ''),
            file_name=doc.get_name(),
            lang=getattr(doc, 'lang', None),
        )
        new_item.set_content(new_content)
        new_item.add_item(css_item)
        out_book.add_item(new_item)
        new_spine.append((new_item.get_id(), 'yes'))

    out_book.spine = new_spine

    # Copy TOC structure
    out_book.toc = source_book.toc

    # Add navigation files
    out_book.add_item(epub.EpubNcx())
    out_book.add_item(epub.EpubNav())

    epub.write_epub(str(output_path), out_book)


# ═══════════════════════════ Translation injection ═══════════════════════════

def _inject_translations(
    doc: epub.EpubHtml,
    pairs: list[AlignedPair],
    granularity: str,
) -> bytes:
    """Inject translation content into a chapter's XHTML.

    For each aligned pair, finds the source paragraph in the DOM using its
    CFI and inserts translation content after it.
    """
    root = parse_item_xml(doc)

    # Build a map: element -> list of (pair, position) for insertion
    # We process pairs in reverse order to avoid offset issues
    insertions: list[tuple[etree._Element, AlignedPair]] = []

    for pair in pairs:
        if not pair.source or not pair.source[0].cfi:
            continue

        source_elem = _resolve_cfi_to_element(pair.source[0].cfi, root)
        if source_elem is not None:
            insertions.append((source_elem, pair))

    # Insert translations after their source elements
    for source_elem, pair in reversed(insertions):
        parent = source_elem.getparent()
        if parent is None:
            continue

        idx = list(parent).index(source_elem)
        ns = _get_namespace(root)

        if granularity == 'sentence':
            container = _build_sentence_pair_html(pair, ns)
        else:
            container = _build_paragraph_pair_html(pair, ns)

        # Insert after the source element
        parent.insert(idx + 1, container)

    # Add bilingual CSS link to head
    _add_css_link(root)

    return etree.tostring(
        root, encoding='unicode', method='xml', xml_declaration=True
    ).encode('utf-8')


def _resolve_cfi_to_element(cfi_str: str, root) -> etree._Element | None:
    """Resolve a CFI string to the target element in an already-parsed DOM.

    Since we already have the root, we only need the redirect portion
    of the CFI to navigate the DOM.
    """
    parsed = CFIParser().parse_epubcfi(cfi_str)
    parent_path = parsed.get('parent', {})
    redirect = parent_path.get('redirect')

    if not redirect:
        return None

    result = resolve_dom_steps(root, redirect)
    if result is None:
        return None

    return result.get('node')


def _get_namespace(root) -> str:
    """Extract the XHTML namespace from the root element."""
    tag = root.tag
    if isinstance(tag, str) and tag.startswith('{'):
        return tag.split('}')[0] + '}'
    return ''


def _build_paragraph_pair_html(
    pair: AlignedPair, ns: str
) -> etree._Element:
    """Build a bilingual pair container for paragraph-level alignment."""
    container = etree.Element(f'{ns}div')
    container.set('class', 'bilingual-pair')

    # Source text
    src_div = etree.SubElement(container, f'{ns}div')
    src_div.set('class', 'source')
    source_text = ' '.join(s.text for s in pair.source)
    src_div.text = source_text

    # Translation text
    tgt_div = etree.SubElement(container, f'{ns}div')
    tgt_div.set('class', 'translation')
    target_text = ' '.join(s.text for s in pair.target)
    tgt_div.text = target_text

    return container


def _build_sentence_pair_html(
    pair: AlignedPair, ns: str
) -> etree._Element:
    """Build sentence-level bilingual pairs."""
    container = etree.Element(f'{ns}div')
    container.set('class', 'bilingual-pair')

    for src_seg in pair.source:
        # Find corresponding target segments (same sentence_idx if available)
        sent_div = etree.SubElement(container, f'{ns}div')
        sent_div.set('class', 'sentence-pair')

        src_p = etree.SubElement(sent_div, f'{ns}p')
        src_p.set('class', 'src-sent')
        src_p.text = src_seg.text

    # Add all target segments
    for tgt_seg in pair.target:
        sent_div = etree.SubElement(container, f'{ns}div')
        sent_div.set('class', 'sentence-pair')

        tgt_p = etree.SubElement(sent_div, f'{ns}p')
        tgt_p.set('class', 'tgt-sent')
        tgt_p.text = tgt_seg.text

    return container


def _add_css_link(root) -> None:
    """Add a <link> to bilingual.css in the <head> of the document."""
    ns = _get_namespace(root)

    # Find <head>
    head = root.find(f'{ns}head')
    if head is None:
        # Try without namespace
        head = root.find('head')
    if head is None:
        return

    link = etree.SubElement(head, f'{ns}link')
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'style/bilingual.css')


def _copy_metadata(src_book: epub.EpubBook, dst_book: epub.EpubBook) -> None:
    """Copy basic metadata from source to destination book."""
    # Identifier
    identifiers = src_book.get_metadata('DC', 'identifier')
    if identifiers:
        val = identifiers[0][0] if isinstance(identifiers[0], tuple) else identifiers[0]
        dst_book.set_identifier(val + '-bilingual')
    else:
        dst_book.set_identifier('bilingual-epub')

    # Title
    titles = src_book.get_metadata('DC', 'title')
    if titles:
        val = titles[0][0] if isinstance(titles[0], tuple) else titles[0]
        dst_book.set_title(f'{val} (Bilingual)')
    else:
        dst_book.set_title('Bilingual Edition')

    # Language
    languages = src_book.get_metadata('DC', 'language')
    if languages:
        val = languages[0][0] if isinstance(languages[0], tuple) else languages[0]
        dst_book.set_language(val)
    else:
        dst_book.set_language('en')
