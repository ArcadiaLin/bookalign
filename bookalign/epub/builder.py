"""Build a sentence-aligned bilingual EPUB."""

from __future__ import annotations

from collections import defaultdict
import html
from pathlib import Path

from ebooklib import epub

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
.empty-target {
  font-style: italic;
  opacity: 0.72;
}
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
    pairs_by_chapter: dict[int, list[AlignedPair]] = defaultdict(list)
    for pair in alignment.pairs:
        chapter_idx = _pair_source_chapter(pair)
        if chapter_idx is None:
            continue
        pairs_by_chapter[chapter_idx].append(pair)

    chapter_items: list[epub.EpubHtml] = []
    for chapter_idx in sorted(pairs_by_chapter):
        doc = source_docs.get(chapter_idx)
        chapter_title = _chapter_title(doc, chapter_idx)
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
            target_class = 'target-sentence empty-target' if not target_text else 'target-sentence'
            target_text = target_text or '[未对齐]'
            body_parts.append(
                ''.join(
                    [
                        '<div class="sentence-pair">',
                        f'<p class="source-sentence">{html.escape(source_text)}</p>',
                        f'<p class="{target_class}">{html.escape(target_text)}</p>',
                        '</div>',
                    ]
                )
            )
        body_parts.append('</section>')

    return ''.join(body_parts)


def _chapter_title(doc: epub.EpubHtml | None, chapter_idx: int) -> str:
    if doc is None:
        return f'Chapter {chapter_idx + 1}'
    title = getattr(doc, 'title', '') or ''
    if title:
        return title
    name = doc.get_name().rsplit('/', 1)[-1]
    return name or f'Chapter {chapter_idx + 1}'


def _pair_sort_key(pair: AlignedPair) -> tuple[int, int, int]:
    chapter_idx = _pair_source_chapter(pair) or 0
    paragraph_idx = _pair_paragraph_index(pair)
    sentence_idx = min(
        (segment.sentence_idx or 0 for segment in pair.source),
        default=0,
    )
    return chapter_idx, paragraph_idx, sentence_idx


def _pair_source_chapter(pair: AlignedPair) -> int | None:
    if pair.source:
        return min(segment.chapter_idx for segment in pair.source)
    return None


def _pair_paragraph_index(pair: AlignedPair) -> int:
    if pair.source:
        return min(segment.paragraph_idx for segment in pair.source)
    return -1


def _join_segment_texts(segments) -> str:
    return ' '.join(segment.text.strip() for segment in segments if segment.text.strip())
