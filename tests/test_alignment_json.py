"""alignment JSON serialization tests."""

from pathlib import Path

from bookalign.alignment_json import load_alignment_result, save_alignment_result
from bookalign.models.types import AlignmentResult, AlignedPair, JumpFragment, Segment, TextSpan


def test_alignment_result_round_trips_through_json(tmp_path: Path):
    alignment = AlignmentResult(
        pairs=[
            AlignedPair(
                source=[
                    Segment(
                        text='原句。',
                        cfi='epubcfi(/6/2)',
                        chapter_idx=1,
                        paragraph_idx=2,
                        sentence_idx=3,
                        paragraph_cfi='epubcfi(/6/2)',
                        text_start=4,
                        text_end=7,
                        raw_html='<p>原句。</p>',
                        element_xpath='/html/body/p[1]',
                        has_jump_markup=True,
                        is_note_like=True,
                        alignment_role='retain',
                        paratext_kind='note_body',
                        filter_reason='note_block',
                        jump_fragments=[
                            JumpFragment(kind='href', text='1', start=2, end=3, href='#note-1'),
                            JumpFragment(kind='id', anchor_id='note-1'),
                        ],
                        spans=[
                            TextSpan(
                                text='原句。',
                                xpath='/html/body/p[1]',
                                text_node_index=0,
                                char_offset=0,
                                source_kind='text',
                                cfi_text_node_index=0,
                                cfi_exact=True,
                            )
                        ],
                    )
                ],
                target=[
                    Segment(
                        text='译句。',
                        cfi='epubcfi(/6/4)',
                        chapter_idx=1,
                        paragraph_idx=2,
                        sentence_idx=3,
                    )
                ],
                score=0.75,
            )
        ],
        source_lang='ja',
        target_lang='zh',
        granularity='sentence',
        extract_mode='filtered_preserve',
        retained_source_segments=[
            Segment(
                text='保留原文注释。',
                cfi='epubcfi(/6/6)',
                chapter_idx=2,
                paragraph_idx=0,
                sentence_idx=0,
                alignment_role='retain',
                paratext_kind='note_body',
                filter_reason='note_block',
            )
        ],
        retained_target_segments=[
            Segment(
                text='保留译文注释。',
                cfi='epubcfi(/6/8)',
                chapter_idx=2,
                paragraph_idx=0,
                sentence_idx=0,
                alignment_role='retain',
                paratext_kind='frontmatter',
                filter_reason='title_class',
            )
        ],
    )

    path = tmp_path / 'alignment.json'
    save_alignment_result(alignment, path)
    restored = load_alignment_result(path)

    assert restored == alignment
