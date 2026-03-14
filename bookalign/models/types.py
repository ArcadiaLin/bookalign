"""核心数据结构：Segment、AlignedPair、AlignmentResult。"""

from dataclasses import dataclass, field


@dataclass
class SpineItem:
    """Spine 项的包装，记录 spine 序号和对应的 EpubHtml。"""
    index: int                  # 在 spine 中的序号
    item: object                # ebooklib.epub.EpubHtml


@dataclass
class Segment:
    """一个可参与对齐的文本单元（段落或句子）"""
    text: str                   # 干净文本（过滤标签后的纯文本）
    cfi: str                    # Range CFI: epubcfi(/6/N!/path,/start:off,/end:off)
    chapter_idx: int            # 所属章节在 spine 中的序号
    paragraph_idx: int          # 段落在章节内的序号
    sentence_idx: int | None    # 句子在段落内的序号（段落级对齐时为 None）
    raw_html: str = ''          # 原始 HTML 片段（用于输出时保留样式）


@dataclass
class AlignedPair:
    """一组对齐结果"""
    source: list[Segment]       # 原文（可能 1~N 个 Segment）
    target: list[Segment]       # 译文（可能 1~M 个 Segment）
    score: float                # 对齐置信度


@dataclass
class AlignmentResult:
    """整本书的对齐结果"""
    pairs: list[AlignedPair]
    source_lang: str
    target_lang: str
    granularity: str            # 'paragraph' | 'sentence'
