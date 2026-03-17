"""Build a sentence-aligned bilingual EPUB."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import html
from pathlib import Path, PurePosixPath
import posixpath
import re

from ebooklib import epub
from lxml import etree

from bookalign.epub.cfi import parse_item_xml, resolve_cfi
from bookalign.epub.reader import get_metadata, get_spine_documents
from bookalign.models.types import AlignmentResult, AlignedPair

_BILINGUAL_CSS = """\
body {
  font-family: serif;
  line-height: 1.7;
  margin: 0;
  padding: 0 1rem 2rem;
}
h1 {
  font-size: 1.4rem;
  margin: 1.5rem 0 1rem;
}
.paragraph-block {
  margin: 1.25rem 0 1.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e2e2;
}
.sentence-pair {
  margin: 0.65rem 0;
}
.source-sentence {
  margin: 0 0 0.15rem;
  font-size: 1rem;
}
.target-sentence {
  margin: 0 0 0 1rem;
  color: #555;
  font-size: 0.96rem;
}
.empty-source,
.empty-target {
  font-style: italic;
  opacity: 0.72;
}
"""
_GENERATED_CHAPTER_NAME_RE = re.compile(
    r'^(?:chapter[_-]?\d+|section\d+|\d{3,4}|cover|title|contents?)$',
    re.IGNORECASE,
)
_PRESERVED_BLOCK_TAGS = frozenset({'p', 'li', 'blockquote', 'dd', 'dt', 'figcaption', 'pre'})
_CJK_LANGS = frozenset({'zh', 'ja', 'ko'})


@dataclass
class _ParagraphInjection:
    chapter_idx: int
    paragraph_idx: int
    paragraph_cfi: str
    sequence: int
    target_texts: list[str] = field(default_factory=list)


def _source_layout_css(layout_direction: str) -> str:
    direction_css = ''
    if layout_direction == 'horizontal':
        direction_css = """\
body,
.main,
body p,
.main p {
  writing-mode: horizontal-tb !important;
  -webkit-writing-mode: horizontal-tb !important;
  -epub-writing-mode: horizontal-tb !important;
  direction: ltr !important;
  text-orientation: mixed !important;
  -webkit-text-orientation: mixed !important;
  -epub-text-orientation: mixed !important;
  text-align: left !important;
  text-align-last: left !important;
  -webkit-text-align-last: left !important;
  -epub-text-align-last: left !important;
}

body p,
.main p {
  text-indent: 0 !important;
}

body ruby,
body rt {
  writing-mode: horizontal-tb !important;
  -webkit-writing-mode: horizontal-tb !important;
  -epub-writing-mode: horizontal-tb !important;
}
"""

    return f"""\
{direction_css}
.bookalign-translation-block {{
  display: block;
  margin: 0.45em 0 1em 0;
  color: #555;
  font-size: 0.95em;
  line-height: 1.8;
  text-align: left;
  text-indent: 0;
}}
"""


def build_bilingual_epub(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
) -> None:
    """Build a generated bilingual EPUB from sentence alignment results."""

    output_path = Path(output_path)
    out_book = epub.EpubBook()

    _copy_metadata(source_book, target_book, out_book)

    css_item = epub.EpubItem(
        uid='bilingual-css',
        file_name='styles/bilingual.css',
        media_type='text/css',
        content=_BILINGUAL_CSS.encode('utf-8'),
    )
    out_book.add_item(css_item)

    source_docs = {spine_idx: doc for spine_idx, doc in get_spine_documents(source_book)}
    target_docs = {spine_idx: doc for spine_idx, doc in get_spine_documents(target_book)}
    pairs_by_chapter: dict[int, list[AlignedPair]] = defaultdict(list)
    for pair in alignment.pairs:
        chapter_idx = _pair_chapter_index(pair)
        if chapter_idx is None:
            continue
        pairs_by_chapter[chapter_idx].append(pair)

    chapter_items: list[epub.EpubHtml] = []
    for display_idx, chapter_idx in enumerate(sorted(pairs_by_chapter), start=1):
        chapter_title = _chapter_title(
            source_docs.get(chapter_idx),
            target_docs.get(chapter_idx),
            display_idx,
        )
        chapter_html = _build_chapter_html(
            chapter_title=chapter_title,
            pairs=pairs_by_chapter[chapter_idx],
        )

        chapter_item = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapters/chapter_{chapter_idx:04d}.xhtml',
            lang=alignment.source_lang,
        )
        chapter_item.set_content(chapter_html)
        chapter_item.add_item(css_item)
        out_book.add_item(chapter_item)
        chapter_items.append(chapter_item)

    out_book.toc = tuple(chapter_items)
    out_book.spine = ['nav', *chapter_items]
    out_book.add_item(epub.EpubNcx())
    out_book.add_item(epub.EpubNav())

    epub.write_epub(str(output_path), out_book)


def build_bilingual_epub_on_source_layout(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
    *,
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
) -> None:
    """Write translations back into the source EPUB layout using source CFI anchors.

    The first version intentionally preserves the original source block content
    and injects translation sibling blocks after the anchored source paragraph.
    """

    output_path = Path(output_path)
    if layout_direction not in {'horizontal', 'source'}:
        raise ValueError(f'Unsupported layout_direction: {layout_direction}')
    css_item = _ensure_css_item(
        source_book,
        uid='bookalign-source-layout-css',
        file_name='styles/bookalign-source-layout.css',
        content=_source_layout_css(layout_direction),
    )
    _update_source_layout_metadata(source_book, target_book)
    if layout_direction == 'horizontal':
        source_book.set_direction('ltr')

    docs = {spine_idx: doc for spine_idx, doc in get_spine_documents(source_book)}
    injections_by_chapter = _collect_paragraph_injections(
        alignment,
        target_lang=alignment.target_lang,
    )

    for doc in docs.values():
        root = _parse_raw_document_xml(doc)
        _preserve_document_head(doc, root)
        _attach_stylesheet_link(doc, css_item.file_name)

    for chapter_idx, injections in injections_by_chapter.items():
        doc = docs.get(chapter_idx)
        if doc is None:
            continue

        root = _parse_raw_document_xml(doc)
        _normalize_layout_root(root, layout_direction=layout_direction)
        changed = False
        for injection in sorted(
            injections,
            key=lambda item: (item.paragraph_idx, item.sequence),
            reverse=True,
        ):
            if _inject_translation_block(
                root=root,
                book=source_book,
                injection=injection,
                target_lang=alignment.target_lang,
                emit_translation_metadata=emit_translation_metadata,
            ):
                changed = True

        if not changed:
            continue

        doc.set_content(
            etree.tostring(
                root,
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=True,
            )
        )

    _ensure_navigation_items(source_book)
    epub.write_epub(str(output_path), source_book)


def _collect_paragraph_injections(
    alignment: AlignmentResult,
    *,
    target_lang: str,
) -> dict[int, list[_ParagraphInjection]]:
    buckets: dict[tuple[int, int], _ParagraphInjection] = {}
    pending_target_only: list[str] = []
    last_key: tuple[int, int] | None = None
    sequence = 0

    for pair in alignment.pairs:
        target_text = _join_segment_texts(pair.target)
        if pair.source:
            source_segments = sorted(
                pair.source,
                key=lambda segment: (
                    segment.chapter_idx,
                    segment.paragraph_idx,
                    segment.sentence_idx or 0,
                ),
            )
            anchor = source_segments[0]
            key = (anchor.chapter_idx, anchor.paragraph_idx)
            injection = buckets.setdefault(
                key,
                _ParagraphInjection(
                    chapter_idx=anchor.chapter_idx,
                    paragraph_idx=anchor.paragraph_idx,
                    paragraph_cfi=anchor.paragraph_cfi or anchor.cfi,
                    sequence=sequence,
                ),
            )
            if pending_target_only:
                for pending in pending_target_only:
                    _append_translation_text(injection.target_texts, pending)
                pending_target_only.clear()
            _append_translation_text(injection.target_texts, target_text)
            last_key = key
            sequence += 1
            continue

        if not target_text:
            continue
        if last_key is None:
            pending_target_only.append(target_text)
            continue
        _append_translation_text(buckets[last_key].target_texts, target_text)

    if pending_target_only and buckets:
        first_key = min(
            buckets,
            key=lambda item: (
                buckets[item].chapter_idx,
                buckets[item].paragraph_idx,
                buckets[item].sequence,
            ),
        )
        buckets[first_key].target_texts = [
            *pending_target_only,
            *buckets[first_key].target_texts,
        ]

    injections_by_chapter: dict[int, list[_ParagraphInjection]] = defaultdict(list)
    for injection in buckets.values():
        if injection.target_texts:
            injection.target_texts = [_join_translation_texts(injection.target_texts, target_lang)]
            injections_by_chapter[injection.chapter_idx].append(injection)
    return injections_by_chapter


def _append_translation_text(target_texts: list[str], text: str) -> None:
    normalized = text.strip()
    if normalized:
        target_texts.append(normalized)


def _join_translation_texts(target_texts: list[str], target_lang: str) -> str:
    normalized = [text.strip() for text in target_texts if text and text.strip()]
    if not normalized:
        return ''
    base_lang = target_lang.split('-', 1)[0].casefold()
    joiner = '' if base_lang in _CJK_LANGS else ' '
    return joiner.join(normalized)


def _inject_translation_block(
    *,
    root,
    book: epub.EpubBook,
    injection: _ParagraphInjection,
    target_lang: str,
    emit_translation_metadata: bool,
) -> bool:
    resolved = resolve_cfi(injection.paragraph_cfi, book, _root=root)
    block = _resolve_block_anchor(resolved)
    if block is None:
        return False

    translation_block = _build_translation_block(
        root=root,
        source_block=block,
        injection=injection,
        target_lang=target_lang,
        emit_translation_metadata=emit_translation_metadata,
    )
    separator_block = _build_translation_separator(root)
    if emit_translation_metadata:
        _remove_existing_translation_blocks(block, injection.paragraph_cfi)
    _insert_after(block, translation_block)
    _insert_after(translation_block, separator_block)
    return True


def _resolve_block_anchor(resolved: dict | None):
    if not resolved:
        return None
    if resolved.get('type') != 'range':
        target = resolved.get('target')
        return target.get('node') if target else None

    start_target = resolved.get('start', {}).get('target')
    end_target = resolved.get('end', {}).get('target')
    start_node = start_target.get('node') if start_target else None
    end_node = end_target.get('node') if end_target else None
    if start_node is None:
        return None
    if end_node is None or start_node is end_node:
        return start_node
    return _lowest_common_ancestor(start_node, end_node)


def _lowest_common_ancestor(start_node, end_node):
    start_ancestors = []
    current = start_node
    while current is not None:
        start_ancestors.append(current)
        current = current.getparent()

    current = end_node
    while current is not None:
        if current in start_ancestors:
            return current
        current = current.getparent()
    return start_node


def _remove_existing_translation_blocks(block, anchor_cfi: str) -> None:
    sibling = block.getnext()
    while sibling is not None and _has_class(sibling, 'bookalign-translation-block'):
        next_sibling = sibling.getnext()
        if sibling.get('data-bookalign-anchor-cfi') == anchor_cfi:
            sibling.getparent().remove(sibling)
            if next_sibling is not None and _is_blank_separator(next_sibling):
                sibling = next_sibling.getnext()
                next_sibling.getparent().remove(next_sibling)
                continue
        sibling = next_sibling


def _build_translation_block(
    *,
    root,
    source_block,
    injection: _ParagraphInjection,
    target_lang: str,
    emit_translation_metadata: bool,
):
    tag = _translation_tag_for_block(source_block)
    block = _make_xhtml_element(root, tag)
    if emit_translation_metadata:
        block.set('class', 'bookalign-translation-block')
        block.set('lang', target_lang)
        block.set('data-bookalign-anchor-cfi', injection.paragraph_cfi)
        block.set('data-bookalign-paragraph', str(injection.paragraph_idx))
    block.text = ''.join(injection.target_texts)
    block.tail = '\n'

    return block


def _build_translation_separator(root):
    block = _make_xhtml_element(root, 'p')
    br = _make_xhtml_element(root, 'br')
    block.append(br)
    block.tail = '\n'
    return block


def _translation_tag_for_block(source_block) -> str:
    tag = _local_tag(source_block.tag)
    if tag in _PRESERVED_BLOCK_TAGS:
        return tag
    return 'div'


def _make_xhtml_element(root, tag: str):
    namespace = etree.QName(root.tag).namespace if isinstance(root.tag, str) else None
    if namespace:
        return etree.Element(f'{{{namespace}}}{tag}')
    return etree.Element(tag)


def _insert_after(anchor, new_element) -> None:
    parent = anchor.getparent()
    if parent is None:
        return
    parent.insert(parent.index(anchor) + 1, new_element)


def _has_class(element, class_name: str) -> bool:
    classes = set((element.get('class') or '').split())
    return class_name in classes


def _local_tag(tag) -> str:
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def _is_blank_separator(element) -> bool:
    return _local_tag(element.tag) == 'p' and len(element) == 1 and _local_tag(element[0].tag) == 'br'


def _normalize_layout_root(root, *, layout_direction: str) -> None:
    if layout_direction != 'horizontal':
        return

    body = _find_body(root)
    if body is None:
        return

    main = next(
        (child for child in body if isinstance(child.tag, str) and _has_class(child, 'main')),
        None,
    )
    if main is not None:
        classes = [token for token in (main.get('class') or '').split() if token != 'vrtl']
        if 'bookalign-horizontal-layout' not in classes:
            classes.append('bookalign-horizontal-layout')
        main.set('class', ' '.join(classes))


def _find_body(root):
    if _local_tag(root.tag) == 'body':
        return root
    for child in root.iter():
        if isinstance(child.tag, str) and _local_tag(child.tag) == 'body':
            return child
    return None


def _parse_raw_document_xml(doc: epub.EpubHtml):
    content = getattr(doc, 'content', None) or doc.get_content()
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(content, parser=parser)
    if isinstance(root.tag, str) and _local_tag(root.tag) == 'html':
        return root
    return parse_item_xml(doc)


def _preserve_document_head(doc: epub.EpubHtml, root) -> None:
    title = _extract_document_title(root)
    if title:
        doc.title = title

    language = _extract_document_language(root)
    if language:
        doc.lang = language

    doc.links = [
        link
        for link in getattr(doc, 'links', [])
        if link.get('rel') != 'stylesheet'
    ]
    for href in _extract_stylesheet_hrefs(root):
        _attach_stylesheet_link(doc, href, href_is_book_path=False)

    doc.metas = _extract_document_metas(root)


def _extract_document_title(root) -> str:
    for element in root.iter():
        if isinstance(element.tag, str) and _local_tag(element.tag) == 'title':
            return (element.text or '').strip()
    return ''


def _extract_document_language(root) -> str:
    if not isinstance(root.tag, str):
        return ''
    return (
        root.get('{http://www.w3.org/XML/1998/namespace}lang')
        or root.get('lang')
        or ''
    ).strip()


def _extract_stylesheet_hrefs(root) -> list[str]:
    hrefs: list[str] = []
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        if _local_tag(element.tag) != 'link':
            continue
        rel = (element.get('rel') or '').casefold()
        href = (element.get('href') or '').strip()
        if rel == 'stylesheet' and href:
            hrefs.append(href)
    return hrefs


def _extract_document_metas(root) -> list[dict[str, str]]:
    metas: list[dict[str, str]] = []
    for element in root.iter():
        if not isinstance(element.tag, str) or _local_tag(element.tag) != 'meta':
            continue
        attrs = {
            key: value
            for key, value in element.attrib.items()
            if value is not None
        }
        if attrs:
            metas.append(attrs)
    return metas


def _attach_stylesheet_link(
    doc: epub.EpubHtml,
    href: str,
    *,
    href_is_book_path: bool = True,
) -> None:
    target_name = href if href_is_book_path else _resolve_href_from_document(doc.get_name(), href)
    relative_href = _relative_href(doc.get_name(), target_name)
    if any(link.get('rel') == 'stylesheet' and link.get('href') == relative_href for link in doc.links):
        return
    doc.add_link(href=relative_href, rel='stylesheet', type='text/css')


def _relative_href(from_name: str, target_name: str) -> str:
    source = PurePosixPath(from_name)
    target = PurePosixPath(target_name)
    return posixpath.relpath(target.as_posix(), start=source.parent.as_posix() or '.')


def _resolve_href_from_document(doc_name: str, href: str) -> str:
    source = PurePosixPath(doc_name)
    joined = posixpath.normpath(posixpath.join(source.parent.as_posix() or '.', href))
    return PurePosixPath(joined).as_posix()


def _ensure_css_item(
    book: epub.EpubBook,
    *,
    uid: str,
    file_name: str,
    content: str,
):
    for item in book.get_items():
        if getattr(item, 'file_name', None) == file_name:
            item.content = content.encode('utf-8')
            return item

    css_item = epub.EpubItem(
        uid=uid,
        file_name=file_name,
        media_type='text/css',
        content=content.encode('utf-8'),
    )
    book.add_item(css_item)
    return css_item


def _update_source_layout_metadata(
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
) -> None:
    source_meta = get_metadata(source_book)
    target_meta = get_metadata(target_book)
    source_title = source_meta['title'] or 'Source Book'
    target_title = target_meta['title'] or 'Target Book'
    source_book.set_title(f'{source_title} / {target_title}')

    identifier = source_meta['title'] or 'bookalign-output'
    source_book.set_identifier(f'{identifier}-source-layout-bilingual')


def _ensure_navigation_items(book: epub.EpubBook) -> None:
    _ensure_toc_uids(book.toc)
    toc_titles = _toc_title_map(book.toc)
    docs = []
    for idx, doc in get_spine_documents(book):
        if not getattr(doc, 'id', None):
            doc.id = f'bookalign-doc-{idx}'
        if not getattr(doc, 'uid', None):
            doc.uid = doc.id
        if not getattr(doc, 'title', None):
            toc_title = toc_titles.get(doc.get_name())
            if toc_title:
                doc.title = toc_title
        docs.append(doc)

    if not book.toc and docs:
        book.toc = tuple(
            epub.Link(
                doc.get_name(),
                _chapter_title(doc, None, display_idx),
                getattr(doc, 'id', None) or f'bookalign-doc-{display_idx}',
            )
            for display_idx, doc in enumerate(docs, start=1)
        )

    items = list(book.get_items())
    if not any(isinstance(item, epub.EpubNcx) for item in items):
        book.add_item(epub.EpubNcx())
    if not any(isinstance(item, epub.EpubNav) for item in items):
        nav_item = epub.EpubNav()
        book.add_item(nav_item)
        spine_entries = list(book.spine)
        if 'nav' not in spine_entries:
            book.spine = ['nav', *spine_entries]


def _toc_title_map(entries) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not entries:
        return mapping

    for entry in entries:
        if isinstance(entry, tuple) and len(entry) == 2:
            section, children = entry
            href = getattr(section, 'href', '')
            title = (getattr(section, 'title', '') or '').strip()
            if href and title:
                mapping[href] = title
            mapping.update(_toc_title_map(children))
            continue

        href = getattr(entry, 'href', '')
        title = (getattr(entry, 'title', '') or '').strip()
        if href and title:
            mapping[href] = title

    return mapping


def _ensure_toc_uids(entries, *, prefix: str = 'toc') -> None:
    if not entries:
        return

    counter = 0

    def walk(nodes) -> None:
        nonlocal counter
        for node in nodes:
            if isinstance(node, tuple) and len(node) == 2:
                section, children = node
                assign_uid(section)
                walk(children)
                continue
            assign_uid(node)

    def assign_uid(node) -> None:
        nonlocal counter
        if not hasattr(node, 'uid'):
            return
        if getattr(node, 'uid', None):
            return

        href = getattr(node, 'href', '') or ''
        title = (getattr(node, 'title', '') or '').strip()
        token = href or title or f'{prefix}-{counter + 1}'
        token = re.sub(r'[^A-Za-z0-9_.-]+', '-', token).strip('-') or f'{prefix}-{counter + 1}'
        counter += 1
        node.uid = f'{prefix}-{counter}-{token}'

    walk(entries)


def _copy_metadata(
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    out_book: epub.EpubBook,
) -> None:
    source_meta = get_metadata(source_book)
    target_meta = get_metadata(target_book)

    identifier = source_meta['title'] or 'bookalign-output'
    out_book.set_identifier(f'{identifier}-sentence-aligned')

    source_title = source_meta['title'] or 'Source Book'
    target_title = target_meta['title'] or 'Target Book'
    out_book.set_title(f'{source_title} / {target_title}')
    out_book.set_language(source_meta['language'] or 'zh')

    author = source_meta['author'] or target_meta['author']
    if author:
        out_book.add_author(author)


def _build_chapter_html(
    *,
    chapter_title: str,
    pairs: list[AlignedPair],
) -> str:
    paragraphs: dict[int, list[AlignedPair]] = defaultdict(list)
    for pair in sorted(pairs, key=_pair_sort_key):
        para_idx = _pair_paragraph_index(pair)
        paragraphs[para_idx].append(pair)

    body_parts = [f'<h1>{html.escape(chapter_title)}</h1>']
    for paragraph_idx in sorted(paragraphs):
        body_parts.append('<section class="paragraph-block">')
        for pair in paragraphs[paragraph_idx]:
            source_text = _join_segment_texts(pair.source)
            target_text = _join_segment_texts(pair.target)
            source_class = 'source-sentence empty-source' if not source_text else 'source-sentence'
            target_class = 'target-sentence empty-target' if not target_text else 'target-sentence'
            source_text = source_text or '[原文缺失]'
            target_text = target_text or '[未对齐]'
            body_parts.append(
                ''.join(
                    [
                        '<div class="sentence-pair">',
                        f'<p class="{source_class}">{html.escape(source_text)}</p>',
                        f'<p class="{target_class}">{html.escape(target_text)}</p>',
                        '</div>',
                    ]
                )
            )
        body_parts.append('</section>')

    return ''.join(body_parts)


def _chapter_title(
    source_doc: epub.EpubHtml | None,
    target_doc: epub.EpubHtml | None,
    display_idx: int,
) -> str:
    doc = source_doc or target_doc
    if doc is None:
        return f'Chapter {display_idx}'
    title = getattr(doc, 'title', '') or ''
    if title and not _looks_like_generated_chapter_name(title):
        return title

    name = doc.get_name().rsplit('/', 1)[-1].rsplit('.', 1)[0]
    if name and not _looks_like_generated_chapter_name(name):
        return name
    return f'Chapter {display_idx}'


def _pair_sort_key(pair: AlignedPair) -> tuple[int, int, int]:
    chapter_idx = _pair_chapter_index(pair) or 0
    paragraph_idx = _pair_paragraph_index(pair)
    sentence_idx = min(
        (
            segment.sentence_idx or 0
            for segment in (pair.source or pair.target)
        ),
        default=0,
    )
    return chapter_idx, paragraph_idx, sentence_idx


def _pair_chapter_index(pair: AlignedPair) -> int | None:
    if pair.source:
        return min(segment.chapter_idx for segment in pair.source)
    if pair.target:
        return min(segment.chapter_idx for segment in pair.target)
    return None


def _pair_paragraph_index(pair: AlignedPair) -> int:
    if pair.source:
        return min(segment.paragraph_idx for segment in pair.source)
    if pair.target:
        return min(segment.paragraph_idx for segment in pair.target)
    return -1


def _join_segment_texts(segments) -> str:
    return ' '.join(segment.text.strip() for segment in segments if segment.text.strip())


def _looks_like_generated_chapter_name(value: str) -> bool:
    return bool(_GENERATED_CHAPTER_NAME_RE.fullmatch(value.strip()))
