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
    parser.add_argument(
        '--builder-mode',
        default='simple',
        choices=('simple', 'source_layout'),
        help='EPUB builder mode. "source_layout" writes translations back into the source EPUB structure.',
    )
    parser.add_argument(
        '--writeback-mode',
        default='paragraph',
        choices=('paragraph', 'inline'),
        help='Source-layout writeback strategy. "inline" rewrites source paragraphs sentence-by-sentence.',
    )
    parser.add_argument(
        '--chapter-match-mode',
        default='structured',
        choices=('structured', 'raw'),
        help='Chapter matching strategy. "raw" disables paratext-aware skip bias.',
    )
    parser.add_argument(
        '--alignment-json-input',
        type=Path,
        help='Load a previously saved alignment JSON and skip chapter matching / Bertalign.',
    )
    parser.add_argument(
        '--alignment-json-output',
        type=Path,
        help='Save the freshly computed alignment result to JSON for later builder-only tests.',
    )
    parser.add_argument(
        '--layout-direction',
        default='horizontal',
        choices=('horizontal', 'source'),
        help='Output reading direction for source-layout EPUBs. Default keeps the merged book horizontal.',
    )
    parser.add_argument(
        '--emit-translation-metadata',
        action='store_true',
        help='Emit debug metadata attributes on injected translation paragraphs.',
    )
    parser.add_argument(
        '--disable-vertical-punctuation-normalization',
        action='store_true',
        help='Keep vertical-form punctuation in target text even when output layout is horizontal.',
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    alignment = run_bilingual_epub_pipeline(
        source_epub_path=Path(args.source_epub),
        target_epub_path=Path(args.target_epub),
        output_path=Path(args.output_epub),
        source_lang=args.source_lang,
        target_lang=args.target_lang,
        builder_mode=args.builder_mode,
        chapter_match_mode=args.chapter_match_mode,
        alignment_json_input_path=args.alignment_json_input,
        alignment_json_output_path=args.alignment_json_output,
        writeback_mode=args.writeback_mode,
        layout_direction=args.layout_direction,
        emit_translation_metadata=args.emit_translation_metadata,
        normalize_vertical_punctuation=not args.disable_vertical_punctuation_normalization,
    )
    print(f'Generated {args.output_epub} with {len(alignment.pairs)} aligned pairs.')


if __name__ == '__main__':
    main()
