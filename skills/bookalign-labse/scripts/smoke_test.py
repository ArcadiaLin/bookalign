"""Exercise the stable Bookalign workflow with lightweight local fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from _bootstrap import ensure_skill_root

ensure_skill_root()

from ebooklib import epub

import api
import service


class StubAligner:
    """Deterministic aligner for installation checks."""

    def align(self, src_texts: list[str], tgt_texts: list[str]) -> list[tuple[list[int], list[int], float]]:
        return [
            ([index], [index], 1.0)
            for index in range(min(len(src_texts), len(tgt_texts)))
        ]


def _build_book(title: str, language: str, chapters: list[tuple[str, str]]) -> epub.EpubBook:
    book = epub.EpubBook()
    book.set_identifier(title)
    book.set_title(title)
    book.set_language(language)

    docs = []
    for index, (chapter_title, body) in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f"chapter{index}.xhtml",
            lang=language,
        )
        chapter.set_content(body)
        book.add_item(chapter)
        docs.append(chapter)

    book.spine = docs
    book.toc = tuple(docs)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    return book


def _write_book(book: epub.EpubBook, path: Path) -> Path:
    epub.write_epub(str(path), book)
    return path


def run_smoke_test() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="bookalign-skill-smoke-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        source_book = _build_book(
            "Source",
            "zh",
            [("第一章", "<p>甲。</p><p>乙。</p>")],
        )
        target_book = _build_book(
            "Target",
            "ja",
            [("第一章", "<p>あ。</p><p>い。</p>")],
        )
        source_extraction = api.extract_book(
            _write_book(source_book, tmpdir_path / "source.epub"),
            language="zh",
        )
        target_extraction = api.extract_book(
            _write_book(target_book, tmpdir_path / "target.epub"),
            language="ja",
        )

        chapters = service.list_book_chapters(source_extraction)
        source_chapter_id = source_extraction.chapters[0].chapter_id
        target_chapter_id = target_extraction.chapters[0].chapter_id
        preview = service.get_chapter_preview(source_extraction, source_chapter_id)
        search = service.search_book_text(source_extraction, "甲")
        alignment = service.align_chapter_pair(
            source_extraction,
            target_extraction,
            source_chapter_id,
            target_chapter_id,
            aligner=StubAligner(),
        )
        summary = service.get_alignment_summary(alignment)
        pairs = service.get_aligned_pairs(alignment, limit=5)

        return {
            "ok": True,
            "chapter_count": len(chapters["chapters"]),
            "preview_text": preview["preview_text"],
            "search_match_count": len(search["matches"]),
            "alignment_pair_count": summary["pair_count"],
            "first_pair_source": pairs["pairs"][0]["source"][0]["text"],
            "first_pair_target": pairs["pairs"][0]["target"][0]["text"],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight Bookalign skill smoke test.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON only.",
    )
    args = parser.parse_args()

    result = run_smoke_test()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Smoke test passed: extraction, inspection, search, and local stub alignment are usable.")


if __name__ == "__main__":
    main()
