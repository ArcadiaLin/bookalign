from __future__ import annotations

import json
from pathlib import Path
import random
import re

import pytest

pytest.importorskip('ebooklib')
pytest.importorskip('lxml')
pytest.importorskip('pysbd')

from lxml import etree

from bookalign.epub.cfi import parse_item_xml, resolve_cfi
from bookalign.epub.debug_report import generate_report
from bookalign.epub.extractor import (
    _collect_text_spans,
    _should_emit_segment,
    collect_debug_spans,
    extract_segments,
    extract_text_from_cfi,
)
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.epub.tag_filters import (
    ExtractAction,
    ElementPolicy,
    TagFilterConfig,
    _local_tag,
    get_extract_action,
    match_element_policy,
    should_skip_element,
)


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


def _xml_root(body: str):
    parser = etree.XMLParser(recover=True)
    return etree.fromstring(body, parser=parser)


def test_tag_filter_matches_policy_actions():
    root = _xml_root(
        """
        <html xmlns:epub="http://www.idpf.org/2007/ops">
          <body>
            <p><ruby>漢<rt>kan</rt><rp>(</rp>字</ruby><br/>続き</p>
            <aside epub:type="footnote">note</aside>
            <a class="noteref" href="#fn1">1</a>
            <section><p>inner</p></section>
          </body>
        </html>
        """
    )
    ruby = root.xpath('.//*[local-name()="ruby"]')[0]
    rt = root.xpath('.//*[local-name()="rt"]')[0]
    br = root.xpath('.//*[local-name()="br"]')[0]
    aside = root.xpath('.//*[local-name()="aside"]')[0]
    note_link = root.xpath('.//*[local-name()="a"]')[0]
    section = root.xpath('.//*[local-name()="section"]')[0]

    assert get_extract_action(ruby, TagFilterConfig()) == ExtractAction.KEEP_CHILDREN_ONLY
    assert get_extract_action(rt, TagFilterConfig()) == ExtractAction.SKIP_ENTIRE
    assert get_extract_action(br, TagFilterConfig()) == ExtractAction.INLINE_BREAK
    assert get_extract_action(aside, TagFilterConfig()) == ExtractAction.SKIP_ENTIRE
    assert get_extract_action(note_link, TagFilterConfig()) == ExtractAction.SKIP_ENTIRE
    assert get_extract_action(section, TagFilterConfig()) == ExtractAction.STRUCTURAL_CONTAINER
    assert match_element_policy(ruby, TagFilterConfig()).tag == 'ruby'


def test_collect_text_spans_applies_policy_actions_consistently():
    root = _xml_root(
        """
        <html xmlns:epub="http://www.idpf.org/2007/ops">
          <body>
            <p>甲<ruby>漢<rt>kan</rt><rp>(</rp>字</ruby><span class="super">注</span><a class="noteref" href="#fn1">1</a><strong>乙</strong><br/>丙</p>
          </body>
        </html>
        """
    )
    paragraph = root.xpath('.//*[local-name()="p"]')[0]
    spans = _collect_text_spans(paragraph, root.getroottree(), TagFilterConfig())

    assert ''.join(span.text for span in spans).strip() == '甲漢字乙 丙'
    assert all('注' not in span.text for span in spans)
    assert all('1' not in span.text for span in spans)


def test_collect_debug_spans_emits_debug_metadata():
    root = _xml_root(
        """
        <html xmlns:epub="http://www.idpf.org/2007/ops">
          <body>
            <p>甲<ruby>漢<rt>kan</rt>字</ruby><br/>乙</p>
          </body>
        </html>
        """
    )
    paragraph = root.xpath('.//*[local-name()="p"]')[0]
    debug_spans = collect_debug_spans(paragraph, TagFilterConfig())

    assert debug_spans
    assert any(span.action == 'KEEP_CHILDREN_ONLY' for span in debug_spans)
    assert any(span.action == 'INLINE_BREAK' for span in debug_spans)


def test_custom_policy_supports_direct_text_only():
    config = TagFilterConfig(
        policies=[
            ElementPolicy(tag='span', classes=frozenset({'dropcap'}), action=ExtractAction.KEEP_DIRECT_TEXT_ONLY, name='dropcap'),
        ],
    )
    root = _xml_root(
        """
        <html>
          <body>
            <p><span class="dropcap">A<i>x</i></span>bc</p>
          </body>
        </html>
        """
    )
    paragraph = root.xpath('.//*[local-name()="p"]')[0]
    spans = _collect_text_spans(paragraph, root.getroottree(), config)

    assert ''.join(span.text for span in spans).strip() == 'Abc'


def test_collect_text_spans_drops_numeric_break_markers():
    root = _xml_root(
        """
        <html>
          <body>
            <p>第一句<br/>3<br/>第二句</p>
          </body>
        </html>
        """
    )
    paragraph = root.xpath('.//*[local-name()="p"]')[0]
    spans = _collect_text_spans(paragraph, root.getroottree(), TagFilterConfig())
    assert ''.join(span.text for span in spans).strip() == '第一句 第二句'


def test_should_emit_segment_skips_obvious_noise_and_headings():
    config = TagFilterConfig()
    root = _xml_root(
        """
        <html>
          <body>
            <p id="license-note">Project Gutenberg trademark license fee</p>
            <h1>CHAPTER I</h1>
            <p>这是正常的正文句子。</p>
          </body>
        </html>
        """
    )
    noisy = root.xpath('.//*[local-name()="p"]')[0]
    heading = root.xpath('.//*[local-name()="h1"]')[0]
    body = root.xpath('.//*[local-name()="p"]')[1]
    assert _should_emit_segment(noisy, 'Project Gutenberg trademark license fee', '<p>...</p>', config) is False
    assert _should_emit_segment(heading, 'CHAPTER I', '<h1>CHAPTER I</h1>', config) is False
    assert _should_emit_segment(body, '这是正常的正文句子。', '<p>这是正常的正文句子。</p>', config) is True


def test_collect_text_spans_inserts_space_between_latin_inline_fragments():
    root = _xml_root(
        """
        <html>
          <body>
            <p><span>works.</span><span>Despite these efforts</span></p>
          </body>
        </html>
        """
    )
    paragraph = root.xpath('.//*[local-name()="p"]')[0]
    spans = _collect_text_spans(paragraph, root.getroottree(), TagFilterConfig())
    assert ''.join(span.text for span in spans).strip() == 'works. Despite these efforts'


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
    if get_extract_action(node, config) != ExtractAction.BLOCK_BREAK:
        return False
    raw_html = etree.tostring(node, encoding='unicode', method='html')
    if not _should_emit_segment(node, text, raw_html, config):
        return False
    return True


def _expected_readable_text(node, config: TagFilterConfig) -> str:
    text = ''.join(span.text for span in _collect_text_spans(node, node.getroottree(), config))
    return SentenceSplitter.normalize_text(text)


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
            roundtrip = extract_text_from_cfi(book, paragraph_segment.cfi, config=config)
            assert roundtrip
            assert roundtrip == paragraph_segment.text

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


@pytest.mark.integration
def test_debug_report_generator_outputs_markdown(tmp_path):
    report = generate_report(
        book_query='kinkaku.epub',
        seed=20260315,
        sample_count=2,
        test_type='mixed',
        granularity='sentence',
        language='ja',
        include_debug=True,
    )
    output = tmp_path / 'report.md'
    output.write_text(report, encoding='utf-8')

    assert '# EPUB Extraction Audit' in report
    assert '## Samples' in report
    assert '#### Debug Spans' in report
