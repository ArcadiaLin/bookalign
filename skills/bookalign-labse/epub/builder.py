"""Build a sentence-aligned bilingual EPUB."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
import html
from pathlib import Path, PurePosixPath
import posixpath
import re

from ebooklib import epub
from lxml import etree

from epub.cfi import parse_item_xml, resolve_cfi
from epub.extractor import (
    _build_span_boundaries,
    _iter_readable_text_parts,
    _normalize_readable_spans,
    _trim_spans,
)
from epub.reader import get_metadata, get_spine_documents
from epub.tag_filters import TagFilterConfig, build_tag_filter_config
from models.types import AlignmentResult, AlignedPair, Segment, TextSpan

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
  text-indent: 2em;
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
_VERTICAL_TO_HORIZONTAL_PUNCTUATION = str.maketrans({
    '︽': '《',
    '︾': '》',
    '︿': '〈',
    '﹀': '〉',
    '︵': '（',
    '︶': '）',
    '﹁': '「',
    '﹂': '」',
    '﹃': '『',
    '﹄': '』',
})
_NOTE_REF_ANCHOR_RE = re.compile(r'^fnref\d+$', re.IGNORECASE)


@dataclass
class _ParagraphInjection:
    chapter_idx: int
    paragraph_idx: int
    paragraph_cfi: str
    sequence: int
    target_texts: list[str] = field(default_factory=list)
    target_segments: list[Segment] = field(default_factory=list)


@dataclass
class SourceLayoutBuilderConfig:
    source_lang: str
    target_lang: str
    extract_mode: str = 'filtered_preserve'
    writeback_mode: str = 'paragraph'
    layout_direction: str = 'horizontal'
    emit_translation_metadata: bool = False
    normalize_vertical_punctuation: bool = True
    note_anchor_map: dict[str, str] = field(default_factory=dict)
    note_ref_anchor_map: dict[str, str] = field(default_factory=dict)
    note_ref_doc_map: dict[str, str] = field(default_factory=dict)
    retained_doc_name: str = 'xhtml/bookalign-note-target.xhtml'
    retained_extra_doc_name: str = 'xhtml/bookalign-retained-extra.xhtml'
    include_note_appendix: bool = True
    include_extra_target_appendix: bool = True
    indent_chinese_paragraphs: bool = True
    chinese_paragraph_indent: str = '  '


@dataclass
class _InlineSentenceUnit:
    source_segments: list[Segment]
    target_text: str
    target_segments: list[Segment]
    sequence: int


@dataclass
class _InlineParagraphRewrite:
    chapter_idx: int
    paragraph_idx: int
    paragraph_cfi: str
    sequence: int
    units: list[_InlineSentenceUnit] = field(default_factory=list)


@dataclass(frozen=True)
class _TextSlotKey:
    owner_path: tuple[int, ...]
    source_kind: str
    text_node_index: int


@dataclass(frozen=True)
class _PreparedPair:
    source_segments: list[Segment]
    target_segments: list[Segment]
    target_text: str


def _toc_entries(toc) -> tuple:
    if toc is None:
        return ()
    if isinstance(toc, (list, tuple)):
        return tuple(toc)
    return (toc,)


def _clean_toc_entries(entries) -> tuple:
    cleaned = []
    for entry in _toc_entries(entries):
        if isinstance(entry, tuple) and len(entry) == 2:
            section, children = entry
            cleaned_children = _clean_toc_entries(children)
            cleaned.append((section, cleaned_children))
            continue
        href = getattr(entry, 'href', '') or ''
        if href:
            cleaned.append(entry)
    return tuple(cleaned)


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
.bookalign-translation-block[lang|="zh"],
.bookalign-retained-target-block[lang|="zh"] {{
  text-indent: 2em;
}}
.bookalign-note-ref-marker {{
  display: inline-block;
  margin-left: 0.08em;
  font-size: 0.72em;
  line-height: 1;
  vertical-align: super;
  font-weight: 600;
  text-decoration: none !important;
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
            target_lang=alignment.target_lang,
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
    writeback_mode: str = 'paragraph',
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
    normalize_vertical_punctuation: bool = True,
    extract_mode: str = 'filtered_preserve',
    include_note_appendix: bool = True,
    include_extra_target_appendix: bool = True,
) -> None:
    """Write translations back into the source EPUB layout using source CFI anchors.

    The first version intentionally preserves the original source block content
    and injects translation sibling blocks after the anchored source paragraph.
    """

    output_path = Path(output_path)
    if layout_direction not in {'horizontal', 'source'}:
        raise ValueError(f'Unsupported layout_direction: {layout_direction}')
    if writeback_mode not in {'paragraph', 'inline'}:
        raise ValueError(f'Unsupported writeback_mode: {writeback_mode}')

    config = SourceLayoutBuilderConfig(
        source_lang=alignment.source_lang,
        target_lang=alignment.target_lang,
        extract_mode=extract_mode,
        writeback_mode=writeback_mode,
        layout_direction=layout_direction,
        emit_translation_metadata=emit_translation_metadata,
        normalize_vertical_punctuation=normalize_vertical_punctuation,
        note_anchor_map=_build_note_anchor_map(alignment),
        note_ref_anchor_map=_build_note_ref_anchor_map(alignment),
        include_note_appendix=include_note_appendix,
        include_extra_target_appendix=include_extra_target_appendix,
    )
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

    strategy = _resolve_source_layout_strategy(config)
    strategy(
        alignment=alignment,
        source_book=source_book,
        docs=docs,
        config=config,
    )
    if extract_mode != 'filtered_preserve':
        raise ValueError(f'Unsupported extract_mode: {extract_mode}')
    _append_retained_target_documents(
        alignment=alignment,
        source_book=source_book,
        config=config,
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
        prepared = _prepare_pair(pair)
        if prepared.source_segments:
            anchor = prepared.source_segments[-1]
            key = _paragraph_anchor_key(anchor)
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
            _append_translation_text(injection.target_texts, prepared.target_text)
            injection.target_segments.extend(prepared.target_segments)
            last_key = key
            sequence += 1
            continue

        if not prepared.target_text:
            continue
        if last_key is None:
            pending_target_only.append(prepared.target_text)
            continue
        _append_translation_text(buckets[last_key].target_texts, prepared.target_text)
        buckets[last_key].target_segments.extend(prepared.target_segments)

    if pending_target_only and buckets:
        first_key = _first_bucket_key(buckets)
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


def _resolve_source_layout_strategy(config: SourceLayoutBuilderConfig):
    language = config.source_lang.split('-', 1)[0].casefold()
    strategies = {
        ('ja', 'paragraph'): _apply_paragraph_source_layout,
        ('ja', 'inline'): _apply_inline_source_layout,
        ('*', 'paragraph'): _apply_paragraph_source_layout,
        ('*', 'inline'): _apply_inline_source_layout,
    }
    return strategies.get((language, config.writeback_mode)) or strategies[('*', config.writeback_mode)]


def _prepare_pair(pair: AlignedPair) -> _PreparedPair:
    source_segments = _sorted_segments(pair.source)
    target_segments = _sorted_segments(pair.target)
    return _PreparedPair(
        source_segments=source_segments,
        target_segments=target_segments,
        target_text=_join_segment_texts(target_segments),
    )


def _sorted_segments(segments: list[Segment]) -> list[Segment]:
    return sorted(segments, key=_segment_sort_key)


def _segment_sort_key(segment: Segment) -> tuple[int, int, int]:
    return (
        segment.chapter_idx,
        segment.paragraph_idx,
        segment.sentence_idx or 0,
    )


def _paragraph_anchor_key(segment: Segment) -> tuple[int, int]:
    return segment.chapter_idx, segment.paragraph_idx


def _first_bucket_key(buckets: dict[tuple[int, int], _ParagraphInjection | _InlineParagraphRewrite]) -> tuple[int, int]:
    return min(
        buckets,
        key=lambda item: (
            buckets[item].chapter_idx,
            buckets[item].paragraph_idx,
            buckets[item].sequence,
        ),
    )


def _apply_paragraph_source_layout(
    *,
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    docs: dict[int, epub.EpubHtml],
    config: SourceLayoutBuilderConfig,
) -> None:
    injections_by_chapter = _collect_paragraph_injections(
        alignment,
        target_lang=config.target_lang,
    )
    for chapter_idx, injections in injections_by_chapter.items():
        doc = docs.get(chapter_idx)
        if doc is None:
            continue

        root = _parse_raw_document_xml(doc)
        _normalize_layout_root(root, layout_direction=config.layout_direction)
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
                config=config,
                current_doc_name=doc.get_name(),
            ):
                changed = True

        if changed:
            _set_document_content(doc, root)


def _apply_inline_source_layout(
    *,
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    docs: dict[int, epub.EpubHtml],
    config: SourceLayoutBuilderConfig,
) -> None:
    rewrites_by_chapter = _collect_inline_paragraph_rewrites(
        alignment,
        target_lang=config.target_lang,
    )
    tag_config = build_tag_filter_config(config.extract_mode)
    for chapter_idx, rewrites in rewrites_by_chapter.items():
        doc = docs.get(chapter_idx)
        if doc is None:
            continue

        root = _parse_raw_document_xml(doc)
        _normalize_layout_root(root, layout_direction=config.layout_direction)
        changed = False
        for rewrite in sorted(
            rewrites,
            key=lambda item: (item.paragraph_idx, item.sequence),
            reverse=True,
        ):
            if _rewrite_inline_paragraph(
                root=root,
                book=source_book,
                rewrite=rewrite,
                config=config,
                tag_config=tag_config,
                current_doc_name=doc.get_name(),
            ):
                changed = True

        if changed:
            _set_document_content(doc, root)


def _append_unmatched_note_segments(
    *,
    alignment: AlignmentResult,
    docs: dict[int, epub.EpubHtml],
    config: SourceLayoutBuilderConfig,
) -> None:
    note_segments = _collect_unmatched_note_segments(alignment)
    if not note_segments or not docs:
        return

    last_chapter_idx = max(docs)
    doc = docs[last_chapter_idx]
    root = _parse_raw_document_xml(doc)
    _normalize_layout_root(root, layout_direction=config.layout_direction)
    body = _find_body(root)
    if body is None:
        return

    appendix = _make_xhtml_element(root, 'div')
    appendix.set('class', 'bookalign-note-appendix')
    heading = _make_xhtml_element(root, 'h2')
    heading.text = '译注附录'
    appendix.append(heading)
    heading.tail = '\n'

    seen: set[tuple[int, int, int | None, str]] = set()
    for segment in note_segments:
        key = (segment.chapter_idx, segment.paragraph_idx, segment.sentence_idx, segment.text)
        if key in seen:
            continue
        seen.add(key)
        paragraph = _make_xhtml_element(root, 'p')
        _render_target_segments_into(
            paragraph,
            root=root,
            segments=[segment],
            config=config,
            current_doc_name=doc.get_name(),
        )
        paragraph.tail = '\n'
        appendix.append(paragraph)

    appendix.tail = '\n'
    body.append(appendix)
    _set_document_content(doc, root)


def _collect_retained_target_blocks(
    alignment: AlignmentResult,
    *,
    include_notes: bool,
) -> list[Segment]:
    retained: list[Segment] = []
    seen: set[tuple[int, int, str, str]] = set()
    for segment in alignment.retained_target_segments:
        if _is_note_segment(segment) != include_notes:
            continue
        key = (
            segment.chapter_idx,
            segment.paragraph_idx,
            segment.paragraph_cfi or segment.cfi,
            segment.raw_html or segment.text,
        )
        if key in seen:
            continue
        seen.add(key)
        retained.append(segment)
    for pair in alignment.pairs:
        if pair.source:
            continue
        for segment in pair.target:
            if _is_note_segment(segment) != include_notes:
                continue
            key = (
                segment.chapter_idx,
                segment.paragraph_idx,
                segment.paragraph_cfi or segment.cfi,
                segment.raw_html or segment.text,
            )
            if key in seen:
                continue
            seen.add(key)
            retained.append(segment)
    return retained


def _is_note_segment(segment: Segment) -> bool:
    return segment.is_note_like or segment.paratext_kind == 'note_body'


def _retained_section_title(paratext_kind: str) -> str:
    return {
        'toc': '目录',
        'note_body': '注释',
        'frontmatter': '前后附文',
        'backmatter': '前后附文',
        'chapter_heading': '章节标题',
        'metadata': '其他保留内容',
    }.get(paratext_kind, '其他保留内容')


def _append_retained_target_documents(
    *,
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    config: SourceLayoutBuilderConfig,
) -> None:
    if config.include_note_appendix:
        _append_retained_target_document(
            alignment=alignment,
            source_book=source_book,
            config=config,
            doc_name=config.retained_doc_name,
            title='译注附录',
            include_notes=True,
        )
    if config.include_extra_target_appendix:
        _append_retained_target_document(
            alignment=alignment,
            source_book=source_book,
            config=config,
            doc_name=config.retained_extra_doc_name,
            title='未对齐译文附录',
            include_notes=False,
        )

def _append_retained_target_document(
    *,
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    config: SourceLayoutBuilderConfig,
    doc_name: str,
    title: str,
    include_notes: bool,
) -> None:
    retained_blocks = _collect_retained_target_blocks(alignment, include_notes=include_notes)
    if not retained_blocks:
        return

    appendix = epub.EpubHtml(
        title=title,
        file_name=doc_name,
        lang=config.target_lang,
    )
    root = etree.fromstring(
        (
            '<?xml version="1.0" encoding="utf-8"?>'
            f'<html xmlns="http://www.w3.org/1999/xhtml">'
            f'<head><title>{html.escape(title)}</title></head>'
            '<body><div class="main"/></body>'
            '</html>'
        ).encode('utf-8'),
        parser=etree.XMLParser(recover=True),
    )
    body = _find_body(root)
    main = next(
        (child for child in body if isinstance(child.tag, str) and _has_class(child, 'main')),
        None,
    )
    if main is None:
        main = _make_xhtml_element(root, 'div')
        main.set('class', 'main')
        body.append(main)

    heading = _make_xhtml_element(root, 'h1')
    heading.text = title
    heading.tail = '\n'
    main.append(heading)

    current_section = None
    for segment in retained_blocks:
        section_title = '注释' if include_notes and _is_note_segment(segment) else _retained_section_title(segment.paratext_kind)
        if section_title != current_section:
            section = _make_xhtml_element(root, 'h2')
            section.text = section_title
            section.tail = '\n'
            main.append(section)
            current_section = section_title

        block = _render_retained_segment_block(
            root=root,
            segment=segment,
            config=config,
            current_doc_name=doc_name,
        )
        block.tail = '\n'
        main.append(block)

    appendix.set_content(
        etree.tostring(
            root,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True,
        )
    )
    _attach_stylesheet_link(appendix, 'styles/bookalign-source-layout.css')
    source_book.add_item(appendix)
    source_book.toc = tuple(
        [
            *_clean_toc_entries(source_book.toc),
            epub.Link(
                appendix.file_name,
                title,
                getattr(appendix, 'id', None) or doc_name,
            ),
        ]
    )
    source_book.spine = [*list(source_book.spine), appendix]
    return


def _render_retained_segment_block(
    *,
    root,
    segment: Segment,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
):
    rendered = _retained_block_from_raw_html(
        root=root,
        segment=segment,
        config=config,
        current_doc_name=current_doc_name,
    )
    if rendered is not None:
        rendered.set('lang', config.target_lang)
        _add_class(rendered, 'bookalign-retained-target-block')
        return rendered

    paragraph = _make_xhtml_element(root, 'p')
    paragraph.set('lang', config.target_lang)
    paragraph.set('class', 'bookalign-retained-target-block')
    if _preserve_target_markup(config):
        _render_target_segments_into(
            paragraph,
            root=root,
            segments=[segment],
            config=config,
            current_doc_name=current_doc_name,
        )
    else:
        paragraph.text = _apply_target_paragraph_indent(
            _normalize_target_text_for_layout(
                segment.text,
                target_lang=config.target_lang,
                config=config,
            ),
            target_lang=config.target_lang,
            config=config,
        )
    return paragraph


def _retained_block_from_raw_html(
    *,
    root,
    segment: Segment,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
):
    raw_html = (segment.raw_html or '').strip()
    if not raw_html:
        return None

    namespace = etree.QName(root.tag).namespace if isinstance(root.tag, str) else None
    wrapper_tag = f'{{{namespace}}}wrapper' if namespace else 'wrapper'
    try:
        wrapper = etree.fromstring(
            f'<wrapper xmlns="{namespace or ""}">{raw_html}</wrapper>'.encode('utf-8'),
            parser=etree.XMLParser(recover=True),
        )
    except etree.XMLSyntaxError:
        return None
    if wrapper is None or not len(wrapper):
        return None

    block = deepcopy(wrapper[0])
    _rewrite_retained_subtree(
        block,
        config=config,
        current_doc_name=current_doc_name,
    )
    if _is_note_segment(segment) and not (block.get('id') or '').strip():
        for anchor_id in _infer_note_anchor_ids(segment):
            mapped_id = config.note_anchor_map.get(anchor_id)
            if mapped_id:
                block.set('id', mapped_id)
                break
    block.tag = block.tag if isinstance(block.tag, str) else wrapper_tag
    return block


def _rewrite_retained_subtree(
    element,
    *,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> None:
    if not isinstance(getattr(element, 'tag', None), str):
        return

    element_id = (element.get('id') or '').strip()
    if element_id:
        mapped_id = config.note_anchor_map.get(element_id)
        if mapped_id:
            element.set('id', mapped_id)
        elif element_id in config.note_ref_anchor_map:
            element.set(
                'id',
                _register_note_ref_anchor(
                    anchor_id=element_id,
                    config=config,
                    current_doc_name=current_doc_name,
                ),
            )

    href = (element.get('href') or '').strip()
    if href:
        rewritten = _rewrite_note_href(
            href,
            config.note_anchor_map,
            note_ref_anchor_map=config.note_ref_anchor_map,
            note_ref_doc_map=config.note_ref_doc_map,
            current_doc_name=current_doc_name,
            appendix_doc_name=config.retained_doc_name if config.extract_mode == 'filtered_preserve' else '',
        )
        if rewritten:
            element.set('href', rewritten)

    if element.text:
        element.text = _normalize_target_text_for_layout(
            element.text,
            target_lang=config.target_lang,
            config=config,
        )
    if element.tail:
        element.tail = _normalize_target_text_for_layout(
            element.tail,
            target_lang=config.target_lang,
            config=config,
        )
    for child in element:
        _rewrite_retained_subtree(
            child,
            config=config,
            current_doc_name=current_doc_name,
        )
    _normalize_note_ref_anchor_node(element)


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


def _build_note_anchor_map(alignment: AlignmentResult) -> dict[str, str]:
    referenced_note_ids: set[str] = set()
    target_segments = [
        *(segment for pair in alignment.pairs for segment in pair.target),
        *alignment.retained_target_segments,
    ]
    for segment in target_segments:
        for fragment in segment.jump_fragments:
            if fragment.kind != 'href' or '#' not in fragment.href:
                continue
            fragment_id = fragment.href.rpartition('#')[2].strip()
            if fragment_id:
                referenced_note_ids.add(fragment_id)
        referenced_note_ids.update(_collect_raw_html_href_ids(segment))
    mapping: dict[str, str] = {}
    counter = 1
    note_segments = [
        *alignment.retained_target_segments,
        *(
            segment
            for pair in alignment.pairs
            for segment in pair.target
            if segment.is_note_like
        ),
    ]
    for segment in note_segments:
        anchor_ids = [
            fragment.anchor_id
            for fragment in segment.jump_fragments
            if (
                fragment.kind == 'id'
                and fragment.anchor_id
                and 'backlink' not in fragment.anchor_id.casefold()
                and not _looks_like_note_ref_anchor_id(fragment.anchor_id)
            )
        ]
        anchor_ids.extend(_infer_note_anchor_ids(segment))
        for anchor_id in anchor_ids:
            if anchor_id not in referenced_note_ids:
                continue
            if anchor_id in mapping:
                continue
            mapping[anchor_id] = f'bookalign-note-{counter:04d}'
            counter += 1
    return mapping


def _collect_raw_html_href_ids(segment: Segment) -> set[str]:
    raw_html = (segment.raw_html or '').strip()
    if not raw_html:
        return set()
    try:
        wrapper = etree.fromstring(
            f'<wrapper>{raw_html}</wrapper>'.encode('utf-8'),
            parser=etree.XMLParser(recover=True),
        )
    except etree.XMLSyntaxError:
        return set()
    href_ids: set[str] = set()
    for node in wrapper.iter():
        if _local_tag(getattr(node, 'tag', None)) != 'a':
            continue
        href = (node.get('href') or '').strip()
        if '#' not in href:
            continue
        fragment = href.rpartition('#')[2].strip()
        if fragment:
            href_ids.add(fragment)
    return href_ids


def _infer_note_anchor_ids(segment: Segment) -> list[str]:
    if not _is_note_segment(segment):
        return []
    inferred: list[str] = []
    seen: set[str] = set()
    for href_id in _collect_raw_html_href_ids(segment):
        candidate = href_id
        for suffix in ('-backlink', '_backlink', 'backlink'):
            if candidate.casefold().endswith(suffix):
                candidate = candidate[: -len(suffix)]
                break
        candidate = candidate.strip()
        if not candidate or candidate == href_id or candidate in seen or _looks_like_note_ref_anchor_id(candidate):
            continue
        inferred.append(candidate)
        seen.add(candidate)
    return inferred


def _looks_like_note_ref_anchor_id(anchor_id: str) -> bool:
    normalized = (anchor_id or '').strip()
    if not normalized:
        return False
    return bool(_NOTE_REF_ANCHOR_RE.match(normalized))


def _build_note_ref_anchor_map(alignment: AlignmentResult) -> dict[str, str]:
    referenced_note_ref_ids: set[str] = set()
    for segment in _iter_note_like_target_segments(alignment):
        for fragment in segment.jump_fragments:
            if fragment.kind != 'href' or '#' not in fragment.href:
                continue
            fragment_id = fragment.href.rpartition('#')[2].strip()
            if fragment_id:
                referenced_note_ref_ids.add(fragment_id)
        referenced_note_ref_ids.update(_collect_raw_html_href_ids(segment))
    mapping: dict[str, str] = {}
    counter = 1
    anchor_segments = [
        *(segment for pair in alignment.pairs for segment in pair.target),
        *alignment.retained_target_segments,
    ]
    for segment in anchor_segments:
        anchor_ids = [
            fragment.anchor_id
            for fragment in segment.jump_fragments
            if fragment.kind == 'id' and fragment.anchor_id
        ]
        anchor_ids.extend(_collect_raw_html_element_ids(segment))
        for anchor_id in anchor_ids:
            if referenced_note_ref_ids and anchor_id not in referenced_note_ref_ids:
                continue
            if anchor_id in mapping:
                continue
            mapping[anchor_id] = f'bookalign-note-ref-{counter:04d}'
            counter += 1
    return mapping


def _collect_raw_html_element_ids(segment: Segment) -> list[str]:
    raw_html = (segment.raw_html or '').strip()
    if not raw_html:
        return []
    try:
        wrapper = etree.fromstring(
            f'<wrapper>{raw_html}</wrapper>'.encode('utf-8'),
            parser=etree.XMLParser(recover=True),
        )
    except etree.XMLSyntaxError:
        return []
    element_ids: list[str] = []
    seen: set[str] = set()
    for node in wrapper.iter():
        element_id = (node.get('id') or '').strip()
        if not element_id or element_id in seen:
            continue
        seen.add(element_id)
        element_ids.append(element_id)
    return element_ids


def _iter_note_like_target_segments(alignment: AlignmentResult):
    for segment in alignment.retained_target_segments:
        if segment.is_note_like or segment.has_jump_markup:
            yield segment
    for pair in alignment.pairs:
        if pair.source:
            continue
        for segment in pair.target:
            if segment.is_note_like or segment.has_jump_markup:
                yield segment


def _collect_unmatched_note_segments(alignment: AlignmentResult) -> list[Segment]:
    collected: list[Segment] = []
    seen: set[tuple[int, int, int | None, str]] = set()
    for pair in alignment.pairs:
        if pair.source:
            continue
        for segment in pair.target:
            if not (segment.is_note_like or segment.has_jump_markup):
                continue
            key = (segment.chapter_idx, segment.paragraph_idx, segment.sentence_idx, segment.text)
            if key in seen:
                continue
            collected.append(segment)
            seen.add(key)
    return collected


def _target_joiner(target_lang: str) -> str:
    return '' if target_lang.split('-', 1)[0].casefold() in _CJK_LANGS else ' '


def _preserve_target_markup(config: SourceLayoutBuilderConfig) -> bool:
    return config.extract_mode == 'filtered_preserve'


def _rewrite_note_href(
    href: str,
    note_anchor_map: dict[str, str],
    *,
    note_ref_anchor_map: dict[str, str] | None = None,
    note_ref_doc_map: dict[str, str] | None = None,
    current_doc_name: str = '',
    appendix_doc_name: str = '',
) -> str:
    normalized = (href or '').strip()
    if '#' not in normalized:
        return normalized
    _, _, fragment = normalized.rpartition('#')
    anchor_id = fragment.strip()
    if not anchor_id:
        return normalized
    mapped = note_anchor_map.get(anchor_id)
    if mapped:
        if appendix_doc_name and current_doc_name and current_doc_name != appendix_doc_name:
            return f'{_relative_href(current_doc_name, appendix_doc_name)}#{mapped}'
        return f'#{mapped}'

    note_ref_anchor_map = note_ref_anchor_map or {}
    note_ref_doc_map = note_ref_doc_map or {}
    mapped_ref = note_ref_anchor_map.get(anchor_id)
    target_doc_name = note_ref_doc_map.get(anchor_id)
    if not mapped_ref or not target_doc_name:
        return normalized
    if current_doc_name and current_doc_name != target_doc_name:
        return f'{_relative_href(current_doc_name, target_doc_name)}#{mapped_ref}'
    return f'#{mapped_ref}'


def _normalize_note_ref_anchor_id(
    anchor_id: str,
    *,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> str:
    if current_doc_name and anchor_id in config.note_ref_anchor_map:
        return _register_note_ref_anchor(
            anchor_id=anchor_id,
            config=config,
            current_doc_name=current_doc_name,
        )
    return config.note_anchor_map.get(anchor_id, anchor_id)


def _is_note_ref_anchor_node(element) -> bool:
    if _local_tag(getattr(element, 'tag', None)) != 'a':
        return False
    href = (element.get('href') or '').strip()
    element_id = (element.get('id') or '').strip()
    return bool(href and '#' in href and (href.rpartition('#')[2] or element_id))


def _anchor_visible_text(element) -> str:
    parts: list[str] = []
    text = ''.join(element.itertext())
    if text:
        parts.append(text)
    return ''.join(parts).strip()


def _normalize_note_ref_anchor_node(element) -> None:
    if _local_tag(getattr(element, 'tag', None)) != 'a':
        return
    has_img_child = any(_local_tag(getattr(child, 'tag', None)) == 'img' for child in element.iterdescendants())
    if not has_img_child:
        return
    for child in list(element):
        element.remove(child)
    class_names = [name for name in (element.get('class') or '').split() if name]
    if 'bookalign-note-ref-marker' not in class_names:
        class_names.append('bookalign-note-ref-marker')
    if class_names:
        element.set('class', ' '.join(class_names))
    element.text = '注'


def _collect_note_ref_marker_specs(
    *,
    segment: Segment,
    root,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> list[tuple[int, object, str]]:
    raw_html = (segment.raw_html or '').strip()
    if not raw_html:
        return []

    namespace = etree.QName(root.tag).namespace if isinstance(root.tag, str) else None
    try:
        wrapper = etree.fromstring(
            f'<wrapper xmlns="{namespace or ""}">{raw_html}</wrapper>'.encode('utf-8'),
            parser=etree.XMLParser(recover=True),
        )
    except etree.XMLSyntaxError:
        return []
    if wrapper is None or not len(wrapper):
        return []

    block = wrapper[0]
    specs: list[tuple[int, object, str]] = []
    text_len = 0

    def add_text(value: str | None) -> None:
        nonlocal text_len
        if not value:
            return
        normalized = _normalize_target_text_for_layout(
            value,
            target_lang=config.target_lang,
            config=config,
        )
        text_len += len(normalized)

    def walk(node) -> None:
        nonlocal text_len
        add_text(node.text)
        for child in node:
            if _is_note_ref_anchor_node(child) and not _anchor_visible_text(child):
                cloned = deepcopy(child)
                cloned.tail = None
                _rewrite_retained_subtree(
                    cloned,
                    config=config,
                    current_doc_name=current_doc_name,
                )
                _normalize_note_ref_anchor_node(cloned)
                mapped_id = (cloned.get('id') or '').strip()
                specs.append((text_len, cloned, mapped_id))
                add_text(child.tail)
                continue
            walk(child)
            add_text(child.tail)

    walk(block)
    return specs


def _collect_note_ref_fallback_nodes(
    *,
    segment: Segment,
    root,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> dict[str, object]:
    raw_html = (segment.raw_html or '').strip()
    if not raw_html:
        return {}

    namespace = etree.QName(root.tag).namespace if isinstance(root.tag, str) else None
    try:
        wrapper = etree.fromstring(
            f'<wrapper xmlns="{namespace or ""}">{raw_html}</wrapper>'.encode('utf-8'),
            parser=etree.XMLParser(recover=True),
        )
    except etree.XMLSyntaxError:
        return {}
    if wrapper is None or not len(wrapper):
        return {}

    nodes: dict[str, object] = {}
    for element in wrapper[0].iter():
        element_id = (element.get('id') or '').strip()
        if not element_id or element_id not in config.note_ref_anchor_map:
            continue

        candidate = None
        if _local_tag(getattr(element, 'tag', None)) == 'a' and (element.get('href') or '').strip():
            candidate = deepcopy(element)
        else:
            for descendant in element.iter():
                if descendant is element:
                    continue
                if _local_tag(getattr(descendant, 'tag', None)) != 'a':
                    continue
                if not (descendant.get('href') or '').strip():
                    continue
                candidate = deepcopy(descendant)
                break
        if candidate is None:
            continue

        _rewrite_retained_subtree(
            candidate,
            config=config,
            current_doc_name=current_doc_name,
        )
        _normalize_note_ref_anchor_node(candidate)
        mapped_id = _register_note_ref_anchor(
            anchor_id=element_id,
            config=config,
            current_doc_name=current_doc_name,
        )
        candidate.set('id', mapped_id)
        nodes[mapped_id] = candidate
    return nodes


def _register_note_ref_anchor(
    *,
    anchor_id: str,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> str:
    mapped = config.note_ref_anchor_map.get(anchor_id)
    if not mapped:
        return anchor_id
    config.note_ref_doc_map.setdefault(anchor_id, current_doc_name)
    return mapped


def _render_target_segments_into(
    parent,
    *,
    root,
    segments: list[Segment],
    config: SourceLayoutBuilderConfig,
    current_doc_name: str = '',
) -> None:
    rendered_segments = [segment for segment in segments if segment.text.strip()]
    if rendered_segments:
        indent = _target_paragraph_indent_prefix(config.target_lang, config)
        if indent:
            _append_piece(parent, indent)
    joiner = _target_joiner(config.target_lang)
    for index, segment in enumerate(rendered_segments):
        _render_target_segment_into(
            parent,
            root=root,
            segment=segment,
            config=config,
            current_doc_name=current_doc_name,
        )
        if joiner and index < len(rendered_segments) - 1:
            _append_piece(parent, joiner)


def _render_target_segment_into(
    parent,
    *,
    root,
    segment: Segment,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str = '',
) -> None:
    anchor_ids = [
        _normalize_note_ref_anchor_id(
            fragment.anchor_id,
            config=config,
            current_doc_name=current_doc_name,
        )
        for fragment in segment.jump_fragments
        if fragment.kind == 'id' and fragment.anchor_id
    ]
    marker_specs = _collect_note_ref_marker_specs(
        segment=segment,
        root=root,
        config=config,
        current_doc_name=current_doc_name,
    )
    fallback_marker_nodes = _collect_note_ref_fallback_nodes(
        segment=segment,
        root=root,
        config=config,
        current_doc_name=current_doc_name,
    )
    consumed_anchor_ids = {anchor_id for _, _, anchor_id in marker_specs if anchor_id}
    pending_anchor_ids = [anchor_id for anchor_id in anchor_ids if anchor_id not in consumed_anchor_ids]

    normalized_text = _normalize_target_text_for_layout(
        segment.text,
        target_lang=config.target_lang,
        config=config,
    )
    href_fragments = sorted(
        [
            fragment
            for fragment in segment.jump_fragments
            if fragment.kind == 'href'
            and fragment.start is not None
            and fragment.end is not None
            and fragment.start < fragment.end
        ],
        key=lambda item: (item.start or 0, item.end or 0),
    )
    cursor = 0
    marker_specs = sorted(marker_specs, key=lambda item: item[0])
    marker_idx = 0

    def append_markers_before(limit: int) -> None:
        nonlocal marker_idx
        while marker_idx < len(marker_specs) and marker_specs[marker_idx][0] < limit:
            _, marker_node, _ = marker_specs[marker_idx]
            _append_piece(parent, deepcopy(marker_node))
            marker_idx += 1

    def append_markers_at(limit: int) -> None:
        nonlocal marker_idx
        while marker_idx < len(marker_specs) and marker_specs[marker_idx][0] == limit:
            _, marker_node, _ = marker_specs[marker_idx]
            _append_piece(parent, deepcopy(marker_node))
            marker_idx += 1

    for fragment in href_fragments:
        start = max(fragment.start or 0, cursor)
        end = min(fragment.end or 0, len(normalized_text))
        append_markers_before(start)
        if start > cursor:
            _append_piece(parent, normalized_text[cursor:start])
            cursor = start
        append_markers_at(start)
        if start < end:
            anchor = _make_xhtml_element(root, 'a')
            if pending_anchor_ids:
                anchor.set('id', pending_anchor_ids.pop(0))
            anchor.set(
                'href',
                _rewrite_note_href(
                    fragment.href,
                    config.note_anchor_map,
                    note_ref_anchor_map=config.note_ref_anchor_map,
                    note_ref_doc_map=config.note_ref_doc_map,
                    current_doc_name=current_doc_name,
                    appendix_doc_name=config.retained_doc_name if config.extract_mode == 'filtered_preserve' else '',
                ),
            )
            anchor.text = normalized_text[start:end]
            _append_piece(parent, anchor)
        cursor = max(cursor, end)
    while marker_idx < len(marker_specs):
        marker_pos, marker_node, _ = marker_specs[marker_idx]
        marker_pos = max(0, min(marker_pos, len(normalized_text)))
        if marker_pos > cursor:
            _append_piece(parent, normalized_text[cursor:marker_pos])
            cursor = marker_pos
        _append_piece(parent, deepcopy(marker_node))
        marker_idx += 1
    if cursor < len(normalized_text):
        _append_piece(parent, normalized_text[cursor:])
    for anchor_id in pending_anchor_ids:
        fallback_marker = fallback_marker_nodes.get(anchor_id)
        if fallback_marker is not None:
            _append_piece(parent, deepcopy(fallback_marker))
            continue
        anchor = _make_xhtml_element(root, 'a')
        anchor.set('id', anchor_id)
        _append_piece(parent, anchor)


def _collect_inline_paragraph_rewrites(
    alignment: AlignmentResult,
    *,
    target_lang: str,
) -> dict[int, list[_InlineParagraphRewrite]]:
    buckets: dict[tuple[int, int], _InlineParagraphRewrite] = {}
    pending_target_only: list[str] = []
    last_key: tuple[int, int] | None = None
    sequence = 0

    for pair in alignment.pairs:
        prepared = _prepare_pair(pair)
        if prepared.source_segments:
            anchor = prepared.source_segments[-1]
            key = _paragraph_anchor_key(anchor)
            rewrite = buckets.setdefault(
                key,
                _InlineParagraphRewrite(
                    chapter_idx=anchor.chapter_idx,
                    paragraph_idx=anchor.paragraph_idx,
                    paragraph_cfi=anchor.paragraph_cfi or anchor.cfi,
                    sequence=sequence,
                ),
            )
            if pending_target_only:
                pending_text = _join_translation_texts(pending_target_only, target_lang)
                if rewrite.units:
                    rewrite.units[-1].target_text = _join_translation_texts(
                        [pending_text, rewrite.units[-1].target_text],
                        target_lang,
                    )
                elif prepared.source_segments:
                    rewrite.units.append(
                        _InlineSentenceUnit(
                            source_segments=prepared.source_segments,
                            target_text=pending_text,
                            target_segments=[],
                            sequence=sequence,
                        )
                    )
                    sequence += 1
                pending_target_only.clear()

            rewrite.units.append(
                _InlineSentenceUnit(
                    source_segments=prepared.source_segments,
                    target_text=prepared.target_text.strip(),
                    target_segments=prepared.target_segments,
                    sequence=sequence,
                )
            )
            last_key = key
            sequence += 1
            continue

        if not prepared.target_text:
            continue
        if last_key is None:
            pending_target_only.append(prepared.target_text)
            continue
        rewrite = buckets[last_key]
        if rewrite.units:
            rewrite.units[-1].target_text = _join_translation_texts(
                [rewrite.units[-1].target_text, prepared.target_text],
                target_lang,
            )

    if pending_target_only and buckets:
        first_key = _first_bucket_key(buckets)
        rewrite = buckets[first_key]
        if rewrite.units:
            rewrite.units[0].target_text = _join_translation_texts(
                [*pending_target_only, rewrite.units[0].target_text],
                target_lang,
            )

    rewrites_by_chapter: dict[int, list[_InlineParagraphRewrite]] = defaultdict(list)
    for rewrite in buckets.values():
        if rewrite.units:
            rewrites_by_chapter[rewrite.chapter_idx].append(rewrite)
    return rewrites_by_chapter


def _inject_translation_block(
    *,
    root,
    book: epub.EpubBook,
    injection: _ParagraphInjection,
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
) -> bool:
    resolved = resolve_cfi(injection.paragraph_cfi, book, _root=root)
    block = _resolve_block_anchor(resolved)
    if block is None:
        return False

    translation_block = _build_translation_block(
        root=root,
        source_block=block,
        injection=injection,
        config=config,
        current_doc_name=current_doc_name,
    )
    separator_block = _build_translation_separator(root)
    if config.emit_translation_metadata:
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
    config: SourceLayoutBuilderConfig,
    current_doc_name: str,
):
    tag = _translation_tag_for_block(source_block)
    block = _make_xhtml_element(root, tag)
    block.set('class', 'bookalign-translation-block')
    block.set('lang', config.target_lang)
    if config.emit_translation_metadata:
        block.set('data-bookalign-anchor-cfi', injection.paragraph_cfi)
        block.set('data-bookalign-paragraph', str(injection.paragraph_idx))
    if _preserve_target_markup(config) and injection.target_segments:
        _render_target_segments_into(
            block,
            root=root,
            segments=injection.target_segments,
            config=config,
            current_doc_name=current_doc_name,
        )
    else:
        block.text = _apply_target_paragraph_indent(
            _normalize_target_text_for_layout(
                ''.join(injection.target_texts),
                target_lang=config.target_lang,
                config=config,
            ),
            target_lang=config.target_lang,
            config=config,
        )
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


def _add_class(element, class_name: str) -> None:
    classes = [item for item in (element.get('class') or '').split() if item]
    if class_name not in classes:
        classes.append(class_name)
    if classes:
        element.set('class', ' '.join(classes))


def _local_tag(tag) -> str:
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def _is_blank_separator(element) -> bool:
    if _local_tag(element.tag) != 'p':
        return False
    if (element.text or '').strip():
        return False
    if len(element) != 1:
        return False
    child = element[0]
    if _local_tag(child.tag) != 'br':
        return False
    if (child.text or '').strip():
        return False
    if (child.tail or '').strip():
        return False
    return True


def _rewrite_inline_paragraph(
    *,
    root,
    book: epub.EpubBook,
    rewrite: _InlineParagraphRewrite,
    config: SourceLayoutBuilderConfig,
    tag_config: TagFilterConfig,
    current_doc_name: str,
) -> bool:
    resolved = resolve_cfi(rewrite.paragraph_cfi, book, _root=root)
    block = _resolve_block_anchor(resolved)
    if block is None:
        return False

    if config.emit_translation_metadata:
        block.set('data-bookalign-writeback', 'inline')
        block.set('data-bookalign-anchor-cfi', rewrite.paragraph_cfi)
        block.set('data-bookalign-paragraph', str(rewrite.paragraph_idx))

    original_block = deepcopy(block)
    spans = _collect_runtime_text_spans(original_block, tag_config)
    if not spans:
        return False

    trimmed_spans, _, _, _, _ = _trim_spans(spans)
    if not trimmed_spans:
        return False

    boundaries = _build_span_boundaries(trimmed_spans)
    path_map = _node_path_map(original_block)
    _clear_block_content(block)
    emitted = False
    for unit_index, unit in enumerate(rewrite.units):
        sentence_range = _sentence_unit_range(unit, rewrite.paragraph_idx)
        if sentence_range is None:
            continue
        sentence_start, sentence_end = sentence_range
        slot_texts, preserved_nodes = _sentence_slot_payload(
            boundaries=boundaries,
            sentence_start=sentence_start,
            sentence_end=sentence_end,
            path_map=path_map,
        )
        sentence_fragment = _build_sentence_fragment(
            original_node=original_block,
            path_map=path_map,
            slot_texts=slot_texts,
            preserved_nodes=preserved_nodes,
        )
        if not sentence_fragment:
            source_text = _join_segment_texts(unit.source_segments)
            if source_text:
                _append_piece(block, source_text)
                emitted = True
        else:
            for piece in sentence_fragment:
                _append_piece(block, piece)
            emitted = True

        if unit.target_text:
            _append_break(block, root)
            if _preserve_target_markup(config) and unit.target_segments:
                _render_target_segments_into(
                    block,
                    root=root,
                    segments=unit.target_segments,
                    config=config,
                    current_doc_name=current_doc_name,
                )
            else:
                _append_piece(
                    block,
                    _normalize_target_text_for_layout(
                        unit.target_text,
                        target_lang=config.target_lang,
                        config=config,
                    ),
                )
            emitted = True
        if unit_index < len(rewrite.units) - 1:
            _append_break(block, root)

    if not emitted:
        return False

    _remove_following_blank_separators(block)
    _insert_after(block, _build_translation_separator(root))
    return True


def _clear_block_content(block) -> None:
    block.text = None
    for child in block:
        child.tail = None
        block.remove(child)


def _node_path_map(root) -> dict[object, tuple[int, ...]]:
    mapping: dict[object, tuple[int, ...]] = {root: ()}

    def walk(node, path: tuple[int, ...]) -> None:
        element_children = [child for child in node if isinstance(child.tag, str)]
        for index, child in enumerate(element_children):
            child_path = (*path, index)
            mapping[child] = child_path
            walk(child, child_path)

    walk(root, ())
    return mapping


def _sentence_unit_range(unit: _InlineSentenceUnit, paragraph_idx: int) -> tuple[int, int] | None:
    relevant = [
        segment
        for segment in unit.source_segments
        if segment.paragraph_idx == paragraph_idx
        and segment.text_start is not None
        and segment.text_end is not None
    ]
    if not relevant:
        return None
    start = min(segment.text_start for segment in relevant if segment.text_start is not None)
    end = max(segment.text_end for segment in relevant if segment.text_end is not None)
    if start is None or end is None or start >= end:
        return None
    return start, end


def _sentence_slot_payload(
    *,
    boundaries,
    sentence_start: int,
    sentence_end: int,
    path_map: dict[object, tuple[int, ...]],
) -> tuple[dict[_TextSlotKey, str], set[tuple[int, ...]]]:
    slot_texts: dict[_TextSlotKey, str] = {}
    preserved_nodes: set[tuple[int, ...]] = {()}
    for span_start, span_end, span in boundaries:
        overlap_start = max(sentence_start, span_start)
        overlap_end = min(sentence_end, span_end)
        if overlap_start >= overlap_end:
            continue
        owner = getattr(span, '_node', None)
        if owner is None:
            continue
        owner_path = path_map.get(owner)
        if owner_path is None:
            continue
        relative_start = overlap_start - span_start
        relative_end = overlap_end - span_start
        text = span.text[relative_start:relative_end]
        key = _TextSlotKey(
            owner_path=owner_path,
            source_kind=span.source_kind,
            text_node_index=span.text_node_index,
        )
        slot_texts[key] = slot_texts.get(key, '') + text
        preserved_nodes.update(_ancestor_paths(owner_path))
        if span.source_kind == 'synthetic-break':
            preserved_nodes.add(owner_path)
    return slot_texts, preserved_nodes


def _collect_runtime_text_spans(element, config: TagFilterConfig) -> list[TextSpan]:
    tree = element.getroottree()
    raw_spans = list(_iter_readable_text_parts(element, tree, config))
    return _normalize_readable_spans(raw_spans, config)


def _ancestor_paths(path: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [path[:idx] for idx in range(len(path) + 1)]


def _build_sentence_fragment(
    *,
    original_node,
    path_map: dict[object, tuple[int, ...]],
    slot_texts: dict[_TextSlotKey, str],
    preserved_nodes: set[tuple[int, ...]],
):
    pieces: list[object] = []
    text_key = _slot_key(path_map[original_node], 'text', 0)
    text = slot_texts.get(text_key, '')
    if text:
        pieces.append(text)

    element_children = [child for child in original_node if isinstance(child.tag, str)]
    for child in element_children:
        child_path = path_map[child]
        child_piece = _build_element_piece(
            original_node=child,
            path_map=path_map,
            slot_texts=slot_texts,
            preserved_nodes=preserved_nodes,
        )
        if child_piece is not None:
            pieces.append(child_piece)

        tail_key = _slot_key(child_path[:-1], 'tail', _tail_slot_index(original_node, child))
        tail_text = slot_texts.get(tail_key, '')
        if tail_text:
            pieces.append(tail_text)
    return pieces


def _build_element_piece(
    *,
    original_node,
    path_map: dict[object, tuple[int, ...]],
    slot_texts: dict[_TextSlotKey, str],
    preserved_nodes: set[tuple[int, ...]],
):
    node_path = path_map[original_node]
    tag = _local_tag(original_node.tag)
    if tag == 'br':
        key = _slot_key(node_path, 'synthetic-break', 0)
        if key in slot_texts:
            clone = _clone_shallow(original_node)
            clone.tail = None
            return clone
        return None
    if tag in {'rt', 'rp'}:
        clone = deepcopy(original_node)
        clone.tail = None
        return clone

    keep_node = node_path in preserved_nodes
    if not keep_node:
        return None

    clone = _clone_shallow(original_node)
    text_key = _slot_key(node_path, 'text', 0)
    clone.text = slot_texts.get(text_key, '')
    element_children = [child for child in original_node if isinstance(child.tag, str)]
    for child in element_children:
        child_piece = _build_element_piece(
            original_node=child,
            path_map=path_map,
            slot_texts=slot_texts,
            preserved_nodes=preserved_nodes,
        )
        if child_piece is not None:
            clone.append(child_piece)

        tail_key = _slot_key(node_path, 'tail', _tail_slot_index(original_node, child))
        tail_text = slot_texts.get(tail_key, '')
        if tail_text:
            if len(clone):
                clone[-1].tail = (clone[-1].tail or '') + tail_text
            else:
                clone.text = (clone.text or '') + tail_text

    if clone.text:
        return clone
    if len(clone):
        return clone
    return None


def _clone_shallow(element):
    clone = etree.Element(element.tag, attrib=dict(element.attrib), nsmap=element.nsmap)
    return clone


def _slot_key(owner_path: tuple[int, ...], source_kind: str, text_node_index: int) -> _TextSlotKey:
    return _TextSlotKey(owner_path=owner_path, source_kind=source_kind, text_node_index=text_node_index)


def _tail_slot_index(parent, child) -> int:
    count = 0
    for current in parent:
        if isinstance(current.tag, str):
            count += 1
        if current is child:
            return count
    return count


def _append_piece(parent, piece) -> None:
    if isinstance(piece, str):
        if len(parent):
            parent[-1].tail = (parent[-1].tail or '') + piece
        else:
            parent.text = (parent.text or '') + piece
        return
    parent.append(piece)
    piece.tail = piece.tail or ''


def _append_break(parent, root) -> None:
    _append_piece(parent, _make_xhtml_element(root, 'br'))


def _normalize_target_text_for_layout(
    text: str,
    *,
    target_lang: str,
    config: SourceLayoutBuilderConfig,
) -> str:
    if not text:
        return ''
    if not config.normalize_vertical_punctuation:
        return text
    if config.layout_direction != 'horizontal':
        return text
    if target_lang.split('-', 1)[0].casefold() != 'zh':
        return text
    return text.translate(_VERTICAL_TO_HORIZONTAL_PUNCTUATION)


def _target_paragraph_indent_prefix(
    target_lang: str,
    config: SourceLayoutBuilderConfig,
) -> str:
    if not config.indent_chinese_paragraphs:
        return ''
    if target_lang.split('-', 1)[0].casefold() != 'zh':
        return ''
    return config.chinese_paragraph_indent


def _apply_target_paragraph_indent(
    text: str,
    *,
    target_lang: str,
    config: SourceLayoutBuilderConfig,
) -> str:
    if not text:
        return text
    indent = _target_paragraph_indent_prefix(target_lang, config)
    if not indent:
        return text
    if text[:1].isspace() or text.startswith('\u3000'):
        return text
    return f'{indent}{text}'


def _remove_following_blank_separators(block) -> None:
    sibling = block.getnext()
    while sibling is not None and _is_blank_separator(sibling):
        next_sibling = sibling.getnext()
        sibling.getparent().remove(sibling)
        sibling = next_sibling


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


def _set_document_content(doc: epub.EpubHtml, root) -> None:
    doc.set_content(
        etree.tostring(
            root,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True,
        )
    )


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
    book.toc = _clean_toc_entries(book.toc)
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
    target_lang: str,
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
            target_text = _apply_target_paragraph_indent(
                target_text,
                target_lang=target_lang,
                config=SourceLayoutBuilderConfig(source_lang='', target_lang=target_lang),
            )
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
