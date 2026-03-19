from bookalign.align.aligner import align_segments, build_aligned_pairs
from bookalign.align.bertalign_adapter import BertalignAdapter
from bookalign.models.types import Segment


def _segment(
    text: str,
    *,
    chapter_idx: int = 0,
    paragraph_idx: int = 0,
    sentence_idx: int | None = None,
) -> Segment:
    return Segment(
        text=text,
        cfi=f'epubcfi(/6/{paragraph_idx + 2})',
        chapter_idx=chapter_idx,
        paragraph_idx=paragraph_idx,
        sentence_idx=sentence_idx,
    )


def test_bertalign_adapter_uses_split_inputs_and_explicit_languages(monkeypatch):
    captured = {}

    class FakeVendorAligner:
        def __init__(self, src, tgt, **kwargs):
            captured['src'] = src
            captured['tgt'] = tgt
            captured['kwargs'] = kwargs
            self.result = [([0], [0]), ([1, 2], [1])]

        def align_sents(self):
            captured['align_called'] = True

    class FakeVendorModule:
        Bertalign = FakeVendorAligner

        @staticmethod
        def configure_model(name, device):
            captured['model_name'] = name
            captured['device'] = device

    monkeypatch.setattr(
        'bookalign.align.bertalign_adapter._load_vendor_module',
        lambda: FakeVendorModule,
    )

    adapter = BertalignAdapter(
        model_name='test-model',
        device='cuda:0',
        src_lang='zh-Hans',
        tgt_lang='en',
        top_k=4,
    )
    beads = adapter.align(['甲。', '乙。', '丙。'], ['A.', 'BC.'])

    assert beads == [([0], [0], 1.0), ([1, 2], [1], 1.0)]
    assert captured['src'] == '甲。\n乙。\n丙。'
    assert captured['tgt'] == 'A.\nBC.'
    assert captured['kwargs']['is_split'] is True
    assert captured['kwargs']['src_lang'] == 'zh'
    assert captured['kwargs']['tgt_lang'] == 'en'
    assert captured['kwargs']['top_k'] == 4
    assert captured['model_name'] == 'test-model'
    assert captured['device'] == 'cuda:0'
    assert captured['align_called'] is True


def test_bertalign_adapter_returns_empty_for_empty_input():
    adapter = BertalignAdapter()
    assert adapter.align([], ['x']) == []
    assert adapter.align(['x'], []) == []


def test_build_aligned_pairs_maps_indices_back_to_segments():
    src_segments = [_segment('s0'), _segment('s1'), _segment('s2')]
    tgt_segments = [_segment('t0'), _segment('t1')]

    pairs = build_aligned_pairs(
        src_segments,
        tgt_segments,
        [([0], [0], 0.9), ([1, 2], [1], 0.7)],
    )

    assert [segment.text for segment in pairs[0].source] == ['s0']
    assert [segment.text for segment in pairs[0].target] == ['t0']
    assert [segment.text for segment in pairs[1].source] == ['s1', 's2']
    assert [segment.text for segment in pairs[1].target] == ['t1']
    assert pairs[1].score == 0.7


def test_align_segments_builds_alignment_result_from_engine():
    class StubAligner:
        def align(self, src_texts, tgt_texts):
            assert src_texts == ['源句1', '源句2']
            assert tgt_texts == ['target 1', 'target 2', 'target 3']
            return [([0], [0, 1], 1.0), ([1], [2], 0.8)]

    src_segments = [
        _segment('源句1', paragraph_idx=0, sentence_idx=0),
        _segment('源句2', paragraph_idx=1, sentence_idx=0),
    ]
    tgt_segments = [
        _segment('target 1', paragraph_idx=0, sentence_idx=0),
        _segment('target 2', paragraph_idx=1, sentence_idx=0),
        _segment('target 3', paragraph_idx=2, sentence_idx=0),
    ]

    result = align_segments(
        src_segments,
        tgt_segments,
        source_lang='ja',
        target_lang='en',
        granularity='sentence',
        aligner=StubAligner(),
    )

    assert result.source_lang == 'ja'
    assert result.target_lang == 'en'
    assert result.granularity == 'sentence'
    assert len(result.pairs) == 2
    assert [segment.text for segment in result.pairs[0].source] == ['源句1']
    assert [segment.text for segment in result.pairs[0].target] == [
        'target 1',
        'target 2',
    ]
    assert result.pairs[1].score == 0.8
