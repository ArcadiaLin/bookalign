"""Markdown audit report generator for EPUB extraction samples."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import random

from lxml import etree

from bookalign.epub.extractor import (
    _should_emit_segment,
    collect_debug_spans,
    extract_segments,
    extract_text_from_cfi,
)
from bookalign.epub.reader import get_spine_documents, read_epub
from bookalign.epub.cfi import parse_item_xml
from bookalign.epub.sentence_splitter import SentenceSplitter
from bookalign.epub.tag_filters import TagFilterConfig, _local_tag, get_extract_action


BOOKS_DIR = Path(__file__).resolve().parents[2] / 'books'


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a Markdown EPUB extraction audit report.')
    parser.add_argument('--book', required=True, help='Book file name, glob pattern, or absolute path.')
    parser.add_argument('--seed', type=int, default=20260315)
    parser.add_argument('--sample-count', type=int, default=5)
    parser.add_argument(
        '--test-type',
        choices=['normal', 'complex', 'ruby', 'footnote', 'mixed'],
        default='mixed',
    )
    parser.add_argument(
        '--granularity',
        choices=['paragraph', 'sentence'],
        default='paragraph',
    )
    parser.add_argument('--language', default='en')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('tests/artifacts/epub_debug_report.md'))
    args = parser.parse_args()

    report = generate_report(
        book_query=args.book,
        seed=args.seed,
        sample_count=args.sample_count,
        test_type=args.test_type,
        granularity=args.granularity,
        language=args.language,
        include_debug=args.debug,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding='utf-8')


def generate_report(
    *,
    book_query: str,
    seed: int,
    sample_count: int,
    test_type: str,
    granularity: str,
    language: str,
    include_debug: bool,
) -> str:
    config = TagFilterConfig()
    splitter = SentenceSplitter(language) if granularity == 'sentence' else None
    book_path = _resolve_book_path(book_query)
    book = read_epub(book_path)
    rng = random.Random(f'{book_path.name}:{seed}:{test_type}:{granularity}')

    rows: list[dict[str, object]] = []
    for chapter_idx, doc in get_spine_documents(book):
        root = parse_item_xml(doc)
        paragraph_segments = extract_segments(book, doc, chapter_idx, config=config)
        sentence_segments = extract_segments(book, doc, chapter_idx, config=config, splitter=splitter) if splitter else []
        sentence_map: dict[int, list[object]] = defaultdict(list)
        for segment in sentence_segments:
            sentence_map[segment.paragraph_idx].append(segment)

        for segment in paragraph_segments:
            element = root.xpath(segment.element_xpath)
            if not element:
                continue
            node = element[0]
            if not _should_emit_segment(
                node,
                segment.text,
                etree.tostring(node, encoding='unicode', method='html'),
                config,
            ):
                continue
            if not _matches_test_type(node, test_type):
                continue
            rows.append(
                {
                    'chapter_idx': chapter_idx,
                    'doc_name': _doc_name(doc),
                    'paragraph_idx': segment.paragraph_idx,
                    'segment': segment,
                    'node': node,
                    'sentences': sentence_map.get(segment.paragraph_idx, []),
                }
            )

    chosen = rng.sample(rows, k=min(sample_count, len(rows))) if rows else []
    summary = _summarize(chosen, book, config)

    lines = [
        '# EPUB Extraction Audit',
        '',
        f'- Book: `{book_path.name}`',
        f'- Seed: `{seed}`',
        f'- Sample count: `{len(chosen)}`',
        f'- Test type: `{test_type}`',
        f'- Granularity: `{granularity}`',
        f'- Debug metadata: `{"on" if include_debug else "off"}`',
        '',
        '## Samples',
        '',
    ]

    for idx, row in enumerate(chosen, start=1):
        segment = row['segment']
        node = row['node']
        sentences = row['sentences']
        roundtrip = extract_text_from_cfi(book, segment.cfi, config=config)
        lines.extend(
            [
                f'### Sample {idx}',
                '',
                f'- Chapter / Paragraph: `{row["chapter_idx"]}` / `{segment.paragraph_idx}`',
                f'- Document: `{row["doc_name"]}`',
                f'- XPath: `{segment.element_xpath}`',
                f'- Action: `{get_extract_action(node, config).name}`',
                f'- CFI roundtrip match: `{"yes" if roundtrip == segment.text else "no"}`',
                '',
                '#### Raw XHTML',
                '',
                '```html',
                etree.tostring(node, encoding='unicode', method='html').strip(),
                '```',
                '',
                '#### Extracted Text',
                '',
                segment.text,
                '',
            ]
        )
        if sentences:
            lines.extend(['#### Sentence Segments', ''])
            for sent in sentences:
                lines.append(f'- `{sent.sentence_idx}`: {sent.text}')
            lines.append('')
        lines.extend(
            [
                '#### CFI Roundtrip',
                '',
                roundtrip or '(empty)',
                '',
            ]
        )
        if include_debug:
            lines.extend(['#### Debug Spans', ''])
            for debug in collect_debug_spans(node, config):
                lines.append(
                    f'- `{debug.tag}` `{debug.action}` `{debug.policy_name}` `{debug.xpath}` {debug.text_preview}'
                )
            lines.append('')
        lines.extend(
            [
                '#### Reviewer Notes',
                '',
                '- Pending external review.',
                '',
            ]
        )

    lines.extend(
        [
            '## Summary',
            '',
            f'- Total samples: `{summary["total"]}`',
            f'- Ruby samples: `{summary["ruby"]}`',
            f'- Footnote-ish samples: `{summary["footnote"]}`',
            f'- Roundtrip mismatches: `{summary["roundtrip_mismatch"]}`',
            '',
            '## Failed Samples',
            '',
        ]
    )
    failed = [idx for idx, row in enumerate(chosen, start=1) if extract_text_from_cfi(book, row['segment'].cfi, config=config) != row['segment'].text]
    if failed:
        for idx in failed:
            lines.append(f'- Sample {idx}')
    else:
        lines.append('- None')
    lines.extend(
        [
            '',
            '## Suggested Fix Directions',
            '',
            '- Inspect any roundtrip mismatch where normalized extracted text diverges from the paragraph segment.',
            '- Review debug spans for over-skipped note links or missed ruby base text.',
            '- Compare paragraph and sentence outputs when inline breaks appear in poetry-like XHTML.',
            '',
        ]
    )
    return '\n'.join(lines)


def _resolve_book_path(book_query: str) -> Path:
    path = Path(book_query)
    if path.exists():
        return path
    matches = sorted(BOOKS_DIR.glob(book_query))
    if not matches:
        matches = sorted(BOOKS_DIR.glob(f'*{book_query}*'))
    if not matches:
        raise FileNotFoundError(f'No EPUB matches: {book_query}')
    return matches[0]


def _doc_name(doc) -> str:
    if hasattr(doc, 'file_name'):
        return getattr(doc, 'file_name')
    if hasattr(doc, 'get_name'):
        return doc.get_name()
    return getattr(doc, 'id', '<unknown>')


def _matches_test_type(node, test_type: str) -> bool:
    descendants = [child for child in node.iterdescendants() if isinstance(child.tag, str)]
    tags = {_local_tag(child.tag) for child in descendants}
    classes = {' '.join(child.get('class', '').split()) for child in descendants}
    flattened_classes = {part for cls in classes for part in cls.split()}
    has_ruby = 'ruby' in tags
    has_footnote = (
        any(token in {'noteref', 'footnote-ref', 'super'} or token.startswith('footnote') for token in flattened_classes)
        or 'aside' in tags
        or 'nav' in tags
        or any((child.get('href') or '').startswith('#fn') for child in descendants)
    )
    if test_type == 'normal':
        return len(descendants) <= 2 and not has_ruby and not has_footnote
    if test_type == 'complex':
        return len(descendants) >= 4
    if test_type == 'ruby':
        return has_ruby
    if test_type == 'footnote':
        return has_footnote
    return True


def _summarize(rows: list[dict[str, object]], book, config: TagFilterConfig) -> dict[str, int]:
    summary = {
        'total': len(rows),
        'ruby': 0,
        'footnote': 0,
        'roundtrip_mismatch': 0,
    }
    for row in rows:
        node = row['node']
        tags = {_local_tag(child.tag) for child in node.iterdescendants() if isinstance(child.tag, str)}
        classes = {' '.join(child.get('class', '').split()) for child in node.iterdescendants() if isinstance(child.tag, str)}
        flattened_classes = {part for cls in classes for part in cls.split()}
        if 'ruby' in tags:
            summary['ruby'] += 1
        if (
            any(token in {'noteref', 'footnote-ref', 'super'} or token.startswith('footnote') for token in flattened_classes)
            or 'aside' in tags
            or 'nav' in tags
        ):
            summary['footnote'] += 1
        if extract_text_from_cfi(book, row['segment'].cfi, config=config) != row['segment'].text:
            summary['roundtrip_mismatch'] += 1
    return summary


if __name__ == '__main__':
    main()
