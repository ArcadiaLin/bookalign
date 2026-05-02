"""Build a bilingual EPUB with explicit intermediate artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_skill_root

ensure_skill_root()

from align.bertalign_adapter import BertalignAdapter  # noqa: E402
from production import run_bilingual_production, write_json  # noqa: E402
import service  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a controlled Bookalign production workflow with persisted artifacts. "
            "Outputs extractions, slice manifest, alignment JSON, diagnostics, review HTML, and the final EPUB."
        ),
    )
    parser.add_argument("--source-epub", required=True, help="Source/original EPUB path.")
    parser.add_argument("--target-epub", required=True, help="Target/translation EPUB path.")
    parser.add_argument("--artifacts-dir", required=True, help="Output artifact directory.")
    parser.add_argument("--source-lang", default="ja", help="Source language code. Default: ja")
    parser.add_argument("--target-lang", default="zh", help="Target language code. Default: zh")
    parser.add_argument(
        "--slice-plan-json",
        type=Path,
        help="Optional JSON file describing explicit chapter mappings and paragraph slice ranges.",
    )
    parser.add_argument(
        "--alignment-json-input",
        type=Path,
        help="Reuse an existing alignment JSON and skip alignment.",
    )
    parser.add_argument(
        "--builder-mode",
        default="source_layout",
        choices=("simple", "source_layout"),
        help='EPUB builder mode. Default: "source_layout".',
    )
    parser.add_argument(
        "--writeback-mode",
        default="paragraph",
        choices=("paragraph", "inline"),
        help='Source-layout writeback strategy. Default: "paragraph".',
    )
    parser.add_argument(
        "--layout-direction",
        default="horizontal",
        choices=("horizontal", "source"),
        help='Reading direction for source-layout output. Default: "horizontal".',
    )
    parser.add_argument(
        "--model-name",
        default="sentence-transformers/LaBSE",
        help="SentenceTransformer model name or local path. Default: sentence-transformers/LaBSE",
    )
    parser.add_argument(
        "--model-backend",
        default="local",
        choices=("local", "hf_inference"),
        help='Alignment backend. Default: "local".',
    )
    parser.add_argument("--device", default="cuda", help='Torch device. Default: "cuda".')
    parser.add_argument(
        "--emit-translation-metadata",
        action="store_true",
        help="Emit debug metadata attributes on injected translation blocks.",
    )
    parser.add_argument(
        "--disable-vertical-punctuation-normalization",
        action="store_true",
        help="Keep vertical-form punctuation in target text.",
    )
    parser.add_argument(
        "--exclude-note-appendix",
        action="store_true",
        help="Do not append retained target notes into a dedicated appendix document.",
    )
    parser.add_argument(
        "--exclude-extra-target-appendix",
        action="store_true",
        help="Do not append non-note retained target content into a dedicated appendix document.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    slice_plan = None
    if args.slice_plan_json is not None:
        slice_plan = json.loads(args.slice_plan_json.read_text(encoding="utf-8"))

    aligner = None
    if args.alignment_json_input is None:
        aligner = BertalignAdapter(
            model_name=args.model_name,
            model_backend=args.model_backend,
            device=args.device,
            src_lang=args.source_lang,
            tgt_lang=args.target_lang,
        )

    outputs = run_bilingual_production(
        source_epub_path=Path(args.source_epub),
        target_epub_path=Path(args.target_epub),
        artifacts_dir=Path(args.artifacts_dir),
        source_lang=args.source_lang,
        target_lang=args.target_lang,
        aligner=aligner,
        slice_plan=slice_plan,
        alignment_json_input_path=args.alignment_json_input,
        builder_mode=args.builder_mode,
        writeback_mode=args.writeback_mode,
        layout_direction=args.layout_direction,
        emit_translation_metadata=args.emit_translation_metadata,
        normalize_vertical_punctuation=not args.disable_vertical_punctuation_normalization,
        include_note_appendix=not args.exclude_note_appendix,
        include_extra_target_appendix=not args.exclude_extra_target_appendix,
    )

    alignment = service.read_alignment_artifact(outputs["alignment_json"], view="stats")
    write_json(Path(args.artifacts_dir) / "alignment_report.json", alignment)
    service.export_review_html_from_artifact(
        outputs["alignment_json"],
        Path(args.artifacts_dir) / "review.html",
    )
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
