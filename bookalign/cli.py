"""Command-line entry point for bilingual EPUB generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from bookalign.pipeline import run_bilingual_epub_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='bookalign',
        description='Align two EPUB books and build a sentence-level bilingual EPUB.',
    )
    parser.add_argument('source_epub', help='Source EPUB path, for example a Chinese book.')
    parser.add_argument('target_epub', help='Target EPUB path, for example a Japanese translation.')
    parser.add_argument('output_epub', help='Output bilingual EPUB path.')
    parser.add_argument('--source-lang', default='ja', help='Source language code. Default: ja')
    parser.add_argument('--target-lang', default='zh', help='Target language code. Default: zh')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    alignment = run_bilingual_epub_pipeline(
        source_epub_path=Path(args.source_epub),
        target_epub_path=Path(args.target_epub),
        output_path=Path(args.output_epub),
        source_lang=args.source_lang,
        target_lang=args.target_lang,
    )
    print(f'Generated {args.output_epub} with {len(alignment.pairs)} aligned pairs.')


if __name__ == '__main__':
    main()
