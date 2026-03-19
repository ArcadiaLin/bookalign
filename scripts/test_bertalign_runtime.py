from __future__ import annotations

import argparse
import faiss
import torch

from bookalign.align.aligner import align_segments_with_bertalign
from bookalign.models.types import Segment


def _segment(text: str, idx: int) -> Segment:
    return Segment(
        text=text,
        cfi=f'epubcfi(/6/{idx + 2})',
        chapter_idx=0,
        paragraph_idx=idx,
        sentence_idx=idx,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Smoke-test the vendored Bertalign runtime.'
    )
    parser.add_argument(
        '--model-name',
        default='sentence-transformers/LaBSE',
        help='SentenceTransformer model id or local path.',
    )
    parser.add_argument(
        '--device',
        default='cuda',
        help='Embedding device to request for Bertalign (for example: cuda, cuda:0, cpu, auto).',
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    print(f'torch_version={torch.__version__}')
    print(f'cuda_available={torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'cuda_device={torch.cuda.get_device_name(0)}')
    print(f'faiss_version={faiss.__version__}')
    print(f'model_name={args.model_name}')
    print(f'requested_device={args.device}')

    source = [
        _segment('两年以后，大兴安岭。', 0),
        _segment('“顺山倒咧——”', 1),
        _segment('随着这声嘹亮的号子，一棵高大的落叶松轰然倒下。', 2),
    ]
    target = [
        _segment('Two years later, the Greater Khingan Mountains.', 0),
        _segment('"Timber..."', 1),
        _segment(
            'Following the loud chant, a tall Dahurian larch crashed to the ground.',
            2,
        ),
    ]

    result = align_segments_with_bertalign(
        source,
        target,
        source_lang='zh',
        target_lang='en',
        granularity='sentence',
        model_name=args.model_name,
        device=args.device,
    )

    print(f'pair_count={len(result.pairs)}')
    for idx, pair in enumerate(result.pairs):
        payload = {
            'index': idx,
            'score': pair.score,
            'source': [segment.text for segment in pair.source],
            'target': [segment.text for segment in pair.target],
        }
        print(payload)

    if not result.pairs:
        raise SystemExit('No alignment pairs produced.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
