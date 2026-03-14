"""对齐引擎的统一接口。"""

from abc import ABC, abstractmethod


class BaseAligner(ABC):
    """对齐引擎的统一接口"""

    @abstractmethod
    def align(
        self,
        src_texts: list[str],
        tgt_texts: list[str],
    ) -> list[tuple[list[int], list[int], float]]:
        """
        对齐两组文本。

        Args:
            src_texts: 原文文本列表（每项为一个段落或句子）
            tgt_texts: 译文文本列表

        Returns:
            [(src_indices, tgt_indices, score), ...]
            src_indices/tgt_indices 是 0-based 索引列表。
            空列表表示该侧无对应（插入/删除）。
        """
