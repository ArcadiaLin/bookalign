from __future__ import annotations

import json
from pathlib import Path
import random
import re

import pytest

pytest.importorskip('ebooklib')
pytest.importorskip('lxml')
pytest.importorskip('pysbd')

from bookalign.epub.extractor import extract_segments, extract_text_from_cfi
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.epub.cfi import parse_item_xml, resolve_cfi
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.epub.tag_filters import TagFilterConfig, _local_tag, should_skip_element
from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / 'books'
ARTIFACT_DIR = ROOT / 'tests' / 'artifacts'
ARTIFACT_PATH = ARTIFACT_DIR / 'epub_extraction_audit.jsonl'
RNG_SEED = 20260314
BOOK_PATTERNS = {
    'ja': 'kinkaku.epub',
    'en': '*Sherlock Holmes*.epub',
    'es': 'Don Quijote*.epub',
    'zh': 'her.epub',
}
SAMPLE_CHAPTERS = 2
SAMPLE_PARAGRAPHS = 2
MIN_TEXT_LENGTH = 20
COMPLEX_NODE_XPATH = """
.//*[
    (
        local-name()='p' or
        local-name()='li' or
        local-name()='blockquote' or
        local-name()='div'
    )
    and count(descendant::*) >= 1
    and string-length(normalize-space(.)) >= 20
    and not(ancestor-or-self::*[local-name()='nav'])
    and not(contains(concat(' ', normalize-space(@class), ' '), ' titlepage '))
    and not(contains(concat(' ', normalize-space(@class), ' '), ' toc '))
    and not(
        local-name()='div' and
        (
            count(*[local-name()='p' or local-name()='div' or local-name()='section' or local-name()='article']) >= 2
        )
    )
]
"""
FORBIDDEN_TEXT_PATTERNS = [
    r'<[^>]+>',
    r'[\r\n\t]',
    r' {2,}',
]


def _book_path(pattern: str) -> Path:
    matches = sorted(BOOKS_DIR.glob(pattern))
    assert matches, f'No EPUB found for pattern: {pattern}'
    return matches[0]


def _doc_name(doc) -> str:
    if hasattr(doc, 'file_name'):
        return getattr(doc, 'file_name')
    if hasattr(doc, 'get_name'):
        return doc.get_name()
    return getattr(doc, 'id', '<unknown>')


def _is_meaningful_candidate(node, config: TagFilterConfig) -> bool:
    text = SentenceSplitter.normalize_text(_expected_readable_text(node, config))
    if len(text) < MIN_TEXT_LENGTH:
        return False
    if should_skip_element(node, config):
        return False
    if _local_tag(node.tag) == 'div':
        direct_blocks = [
            child for child in node
            if isinstance(child.tag, str)
            and _local_tag(child.tag) in config.block_tags
            and not should_skip_element(child, config)
        ]
        if len(direct_blocks) >= 2:
            return False
    return True


def _expected_readable_text(node, config: TagFilterConfig) -> str:
    parts: list[str] = []

    def walk(element):
        if should_skip_element(element, config):
            return
        if element.text:
            parts.append(element.text)
        for child in element:
            if not isinstance(child.tag, str):
                if child.tail:
                    parts.append(child.tail)
                continue
            if not should_skip_element(child, config) and _local_tag(child.tag) not in config.block_tags:
                walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(node)
    return SentenceSplitter.normalize_text(''.join(parts))


def _select_sample_nodes(book, book_path: Path, config: TagFilterConfig) -> list[tuple[int, object, object]]:
    rng = random.Random(f'{RNG_SEED}:{book_path.name}')
    docs = get_spine_documents(book)
    doc_candidates: list[tuple[int, object, list[object]]] = []

    for chapter_idx, doc in docs:
        root = parse_item_xml(doc)
        nodes = [
            node for node in root.xpath(COMPLEX_NODE_XPATH)
            if isinstance(node.tag, str) and _is_meaningful_candidate(node, config)
        ]
        if nodes:
            doc_candidates.append((chapter_idx, doc, nodes))

    assert doc_candidates, f'No complex paragraph candidates found in {book_path.name}'

    chosen_docs = rng.sample(doc_candidates, k=min(SAMPLE_CHAPTERS, len(doc_candidates)))
    samples: list[tuple[int, object, object]] = []
    for chapter_idx, doc, nodes in chosen_docs:
        chosen_nodes = rng.sample(nodes, k=min(SAMPLE_PARAGRAPHS, len(nodes)))
        for node in chosen_nodes:
            samples.append((chapter_idx, doc, node))
    return samples


def _append_audit_rows(rows: list[dict]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')


@pytest.mark.integration
def test_extract_segments_audits_complex_multilingual_epubs():
    config = TagFilterConfig()
    audit_rows: list[dict] = []

    for language, pattern in BOOK_PATTERNS.items():
        book_path = _book_path(pattern)
        book = read_epub(book_path)
        samples = _select_sample_nodes(book, book_path, config)
        splitter = SentenceSplitter(language=language)
        paragraph_cache: dict[str, dict[str, object]] = {}
        sentence_cache: dict[str, dict[int, list[object]]] = {}

        for chapter_idx, doc, node in samples:
            doc_name = _doc_name(doc)
            if doc_name not in paragraph_cache:
                paragraph_segments = extract_segments(book, doc, chapter_idx, config=config)
                sentence_segments = extract_segments(book, doc, chapter_idx, config=config, splitter=splitter)
                paragraph_cache[doc_name] = {
                    f'{segment.text}\n{segment.raw_html}': segment for segment in paragraph_segments
                }
                grouped: dict[int, list[object]] = {}
                for segment in sentence_segments:
                    grouped.setdefault(segment.paragraph_idx, []).append(segment)
                for grouped_segments in grouped.values():
                    grouped_segments.sort(key=lambda segment: segment.sentence_idx or 0)
                sentence_cache[doc_name] = grouped

            expected_text = _expected_readable_text(node, config)
            expected_html = etree.tostring(node, encoding='unicode', method='html')
            paragraph_segment = paragraph_cache[doc_name].get(f'{expected_text}\n{expected_html}')

            assert paragraph_segment is not None, f'Missing paragraph segment for {doc_name}'
            sentence_segments = sentence_cache[doc_name].get(paragraph_segment.paragraph_idx, [])

            assert paragraph_segment.cfi.startswith('epubcfi('), f'Missing CFI for {doc_name}'
            assert paragraph_segment.spans, f'Missing spans for {doc_name}'
            assert ''.join(span.text for span in paragraph_segment.spans) == paragraph_segment.text

            assert paragraph_segment.text == expected_text

            for pattern_text in FORBIDDEN_TEXT_PATTERNS:
                assert re.search(pattern_text, paragraph_segment.text) is None, (
                    f'Unexpected dirty text pattern {pattern_text!r} in {doc_name}: {paragraph_segment.text!r}'
                )

            resolved = resolve_cfi(paragraph_segment.cfi, book)
            assert resolved is not None, f'Unable to resolve CFI for {doc_name}'
            assert extract_text_from_cfi(book, paragraph_segment.cfi, config=config)

            joiner = '' if language in {'ja', 'zh'} else ' '
            reconstructed = SentenceSplitter.normalize_text(
                joiner.join(segment.text for segment in sentence_segments)
            )
            assert sentence_segments, f'No sentence segments for {doc_name}'
            expected_reconstructed = paragraph_segment.text
            if language in {'ja', 'zh'}:
                reconstructed = reconstructed.replace(' ', '')
                expected_reconstructed = expected_reconstructed.replace(' ', '')
            assert reconstructed == expected_reconstructed
            assert all(segment.cfi.startswith('epubcfi(') for segment in sentence_segments)

            audit_rows.append(
                {
                    'language': language,
                    'book': book_path.name,
                    'chapter_idx': chapter_idx,
                    'doc_name': doc_name,
                    'cfi': paragraph_segment.cfi,
                    'raw_html_excerpt': paragraph_segment.raw_html[:300],
                    'paragraph_text': paragraph_segment.text,
                    'sentences': [segment.text for segment in sentence_segments],
                }
            )

    _append_audit_rows(audit_rows)
