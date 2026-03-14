# BookAlign — 双语 EPUB 对齐与重建 · 项目实施方案

## 1. 项目概述

### 1.1 目标

将一部作品的**原版 EPUB** 和**人工译版 EPUB** 进行句段对齐，输出一本可在阅读器中直接打开的**双语 EPUB**。

### 1.2 应用场景

语言学习中的文学阅读。用户希望同时看到原文与正式译文，而非机器翻译。现有工具大多依赖实时机翻，无法满足对文学措辞、语气和节奏的要求。

### 1.3 支持的对齐粒度

| 粒度 | 说明 | 渲染方式 |
|------|------|---------|
| **段落级** | 一段原文 + 一段译文 | 保留原书节奏，近似常见双语展示 |
| **句子级** | 原句 + 对应译句，段落间加大间距 | 更精细的逐句对照，利于精读 |

---

## 2. 整体架构

### 2.1 模块划分

```
bookalign/                        # Python 包根
├── __init__.py
├── cli.py                        # CLI 入口（click）
├── pipeline.py                   # 主流水线：串联所有模块
│
├── models/
│   ├── __init__.py
│   └── types.py                  # 核心数据结构
│
├── epub/
│   ├── __init__.py
│   ├── reader.py                 # EPUB → 章节文档列表 + 元数据
│   ├── extractor.py              # XHTML → Segment 列表（含标签过滤）
│   ├── cfi.py                    # EPUB CFI 解析与生成
│   ├── sentence_splitter.py      # 多语言句子切分统一接口
│   ├── tag_filters.py            # XHTML 标签过滤规则定义
│   └── builder.py                # 双语 EPUB 重建与输出
│
├── align/
│   ├── __init__.py
│   ├── embedder.py               # Embedding 统一接口（默认 LaBSE）
│   ├── base.py                   # 对齐器抽象基类 BaseAligner
│   ├── vecalign_adapter.py       # vecalign → 内存可调用的对齐器
│   ├── bertalign_adapter.py      # bertalign 适配器
│   └── aligner.py                # 对齐调度入口
│
└── vendor/
    └── vecalign/                 # 原始 vecalign 源码（最小改动）
        ├── __init__.py
        ├── vecalign.py
        ├── dp_utils.py
        ├── dp_core.pyx
        └── overlap.py
```

项目根目录补充：
```
tests/                            # 测试
├── test_extractor.py
├── test_splitter.py
├── test_aligner.py
└── test_builder.py
```

### 2.2 端到端数据流

```
原版 EPUB ─→ reader ─→ extractor ─→ list[Segment] ─┐
                            ↑                         │
                     tag_filters                      ├─→ aligner ─→ AlignmentResult ─→ builder ─→ 双语 EPUB
                     splitter (句子级时)               │
译版 EPUB ─→ reader ─→ extractor ─→ list[Segment] ─┘
```

### 2.3 模块职责一览

| 模块 | 输入 | 输出 | 职责 |
|------|------|------|------|
| `reader` | EPUB 文件路径 | `EpubBook` + 按 spine 排序的文档列表 | 读取与解包 |
| `tag_filters` | — | 过滤规则集 | 定义哪些 XHTML 标签应跳过/保留 |
| `extractor` | XHTML 文档 + 过滤规则 + 切分器 | `list[Segment]` | 文本抽取与定位 |
| `sentence_splitter` | 段落文本 + 语言 | `list[str]` | 句子边界检测 |
| `cfi` | XHTML 元素 + 偏移 | CFI 字符串 | 精确文本定位（句子级时使用）|
| `embedder` | `list[str]` | `ndarray[N, dim]` | 跨语言句子向量化 |
| `aligner` | 两组 Segment | `AlignmentResult` | 调度对齐引擎 |
| `vecalign_adapter` | 文本列表 + embedding | 对齐索引对 | vecalign 的内存调用封装 |
| `bertalign_adapter` | 文本列表 | 对齐索引对 | bertalign 调用封装 |
| `builder` | AlignmentResult + 原书 | EPUB 文件 | 双语内容重建与输出 |

---

## 3. 核心数据结构

文件：`bookalign/models/types.py`

```python
from dataclasses import dataclass, field


@dataclass
class TextSpan:
    """XHTML 中一段连续文本及其在原始文档中的定位"""
    text: str                   # 该片段的文本内容
    xpath: str                  # 所在元素的 XPath
    text_node_index: int        # 元素下第几个文本节点（0-based）
    char_offset: int            # 在该文本节点内的字符偏移

@dataclass
class Segment:
    """一个可参与对齐的文本单元（段落或句子）"""
    text: str                   # 干净文本（过滤标签后的纯文本）
    chapter_idx: int            # 所属章节在 spine 中的序号
    paragraph_idx: int          # 段落在章节内的序号
    sentence_idx: int | None    # 句子在段落内的序号（段落级对齐时为 None）
    spans: list[TextSpan] = field(default_factory=list)
                                # 该文本对应的原始 XHTML 位置
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
```

---

## 4. 各模块详细设计

### 4.1 EPUB 读取 — `epub/reader.py`

**基于现有代码**：`epub/read_book.py` 中的 `read_book()` 和 `get_document()` 可直接迁移。

```python
def read_epub(path: Path) -> epub.EpubBook:
    """读取 EPUB 文件"""

def get_spine_documents(book: epub.EpubBook) -> list[tuple[int, epub.EpubHtml]]:
    """按 spine 顺序返回 (chapter_idx, 文档) 列表
    跳过非 XHTML 项（如 CSS、图片）"""

def get_metadata(book: epub.EpubBook) -> dict:
    """提取元数据：title, author, language, identifier"""
```

### 4.2 XHTML 标签过滤 — `epub/tag_filters.py`

独立模块，将过滤规则从抽取逻辑中解耦，便于按书籍特点定制。

**现有可复用代码**：`bookalign_cfi_v2.py` 第 514-515 行：
```python
_SKIP_TAGS = frozenset({'rt', 'rp'})
_INCLUDE_CHILD_TEXT_TAGS = frozenset({'ruby'})
```

**泛化设计**：

```python
@dataclass
class TagFilterConfig:
    """XHTML 标签过滤配置"""

    # 完全跳过（不抽取任何文本）的标签
    skip_tags: set[str] = field(default_factory=lambda: {
        'rt',             # ruby 注音文本
        'rp',             # ruby 括号标记
        'script',         # 脚本
        'style',          # 样式
    })

    # 带有这些 class 属性的元素将被跳过
    skip_classes: set[str] = field(default_factory=lambda: {
        'super',          # 上标注释标号（如 ＊一）
        'noteref',        # 脚注引用
        'footnote-ref',   # 脚注引用（另一种写法）
        'annotation',     # 注释
    })

    # 块级元素——用作段落边界
    block_tags: set[str] = field(default_factory=lambda: {
        'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'li', 'section', 'article',
    })

def should_skip_element(element, config: TagFilterConfig) -> bool:
    """判断元素是否应在文本抽取中被跳过"""
    tag = etree.QName(element.tag).localname if isinstance(element.tag, str) else None
    if tag in config.skip_tags:
        return True
    classes = set(element.get('class', '').split())
    if classes & config.skip_classes:
        return True
    return False
```

**标签过滤示例**：

| 原始 HTML | 期望抽取 | 规则 |
|-----------|---------|------|
| `金閣<span class="super">＊一</span>のこと` | `金閣のこと` | 跳过 class="super" |
| `<ruby>舞鶴<rt>まいづる</rt></ruby>から` | `舞鶴から` | 跳过 rt，保留 ruby 主体 |
| `<em>重要</em>な文` | `重要な文` | 保留 em 内文本 |

### 4.3 XHTML 文本抽取 — `epub/extractor.py`

**这是整个项目最关键的模块。** 将 XHTML 文档转换为带位置信息的 Segment 列表。

**现有可复用代码**：`bookalign_cfi_v2.py` 第 518-562 行的 `_child_readable_text()` 和 `_readable_segments()` 函数——递归遍历子元素 + 跳过 rt 的核心逻辑可直接迁移。

```python
def extract_segments(
    doc: epub.EpubHtml,
    chapter_idx: int,
    config: TagFilterConfig,
    splitter: SentenceSplitter | None = None,
) -> list[Segment]:
    """
    从 XHTML 文档中抽取文本段落，返回 Segment 列表。

    Args:
        doc: EPUB XHTML 文档
        chapter_idx: 章节在 spine 中的序号
        config: 标签过滤配置
        splitter: 句子切分器。为 None 时返回段落级 Segment。

    Returns:
        list[Segment]，每个 Segment 包含干净文本和原始位置映射。
    """
```

**核心实现逻辑**：

```
遍历 DOM：
  for 每个块级元素 (p, div, h1-h6 ...) as paragraph:
      spans: list[TextSpan] = []

      for node in paragraph.iter():  # 深度优先遍历
          if should_skip_element(node, config):
              # 跳过该元素的 text，但仍处理 tail
              if node.tail:
                  spans.append(TextSpan(text=node.tail, ...))
              continue

          if node.text:
              spans.append(TextSpan(text=node.text, xpath=..., ...))

          # tail 属于父元素的文本流
          if node.tail and node != paragraph:
              spans.append(TextSpan(text=node.tail, ...))

      clean_text = ''.join(s.text for s in spans).strip()
      if not clean_text:
          continue  # 跳过空段落

      if splitter is None:
          # 段落级：整个段落作为一个 Segment
          yield Segment(text=clean_text, chapter_idx=..., paragraph_idx=...,
                        sentence_idx=None, spans=spans, raw_html=tostring(paragraph))
      else:
          # 句子级：切分段落，并将句子映射回对应的 TextSpan
          sentences = splitter.split(clean_text)
          for sent_idx, sent_text in enumerate(sentences):
              sent_spans = _map_sentence_to_spans(sent_text, spans)
              yield Segment(text=sent_text, ..., sentence_idx=sent_idx,
                            spans=sent_spans, raw_html=...)
```

**`_map_sentence_to_spans` 的实现思路**：

句子切分后，需要知道每个句子对应原始 XHTML 中的哪些 TextSpan。方法：

1. 将所有 span 的文本拼接成一个完整字符串
2. 记录每个 span 在拼接字符串中的 `[start, end)` 区间
3. 句子文本在拼接字符串中定位其 `[sent_start, sent_end)` 区间
4. 与 span 区间做交集，得到该句子覆盖的 TextSpan 子集

### 4.4 句子切分 — `epub/sentence_splitter.py`

**统一接口，多语言后端**：

```python
class SentenceSplitter:
    """多语言句子边界检测器"""

    def __init__(self, language: str):
        """
        Args:
            language: ISO 639-1 语言代码，如 'ja', 'zh', 'en', 'es'
        """
        self.language = language
        self._backend = self._init_backend(language)

    def split(self, text: str) -> list[str]:
        """将段落文本切分为句子列表"""
        sentences = self._backend(text)
        return [s.strip() for s in sentences if s.strip()]

    def _init_backend(self, lang: str):
        """根据语言选择最优切分后端"""
        if lang == 'ja':
            return self._split_ja
        elif lang == 'zh':
            return self._split_zh
        else:
            return self._split_pysbd
```

**各语言切分策略**：

| 语言 | 主要断句符号 | 特殊规则 | 后端 |
|------|------------|---------|------|
| `ja` | `。` `！` `？` | 右括号/引号后断句 `」` `）`；对话体 `「…」` 不在引号内断；省略号 `……` 不断 | PySBD(ja) + 自定义后处理 |
| `zh` | `。` `！` `？` | 类似 ja，但引号为 `""` `''`；`……` `——` 不断 | PySBD(zh) |
| `en` | `.` `!` `?` | 缩写（Mr./Dr./etc.）不断；省略号不断 | PySBD(en) |
| `es` | `.` `!` `?` | 倒问号 `¿...?` 和倒感叹号 `¡...!` 成对匹配；缩写处理 | PySBD(es) |
| 其他 | PySBD 默认规则 | — | PySBD(语言代码) |

**PySBD 基础用法**：
```python
import pysbd
seg = pysbd.Segmenter(language="ja", clean=False)
seg.segment("幼時から父は、私によく、金閣のことを語った。父の故郷は...")
# → ['幼時から父は、私によく、金閣のことを語った。', '父の故郷は...']
```

**扩展机制**：语言特化的切分器通过注册方式添加，核心接口保持 `split(text) → list[str]` 不变。日文高精度场景可切换到 `ja_sentence_segmenter` 或 `bunkai`。

### 4.5 CFI 解析与生成 — `epub/cfi.py`

基于现有 `bookalign_cfi_v2.py` 精简重构。**Phase 1 不是关键路径**——段落级对齐通过 XPath 即可定位。句子级对齐时，CFI 可提供更精确的字符级定位。

保留的核心能力：
- `parse_epubcfi(cfi_string)` → 解析 CFI 为结构化数据
- `resolve_cfi(book, cfi)` → 定位到具体元素 + 文本偏移
- `generate_cfi(element, offset)` → 从元素位置生成 CFI 字符串

### 4.6 Embedding — `align/embedder.py`

#### 4.6.1 为什么用 LaBSE 替代 LASER

| 维度 | LASER | LaBSE |
|------|-------|-------|
| Python 3.12+ 兼容性 | ❌ 依赖 fairseq，无法导入 | ✅ sentence-transformers 完全兼容 |
| 双文检索 F1 (Bible) | 0.58 | **0.72** |
| XTREME 基准 (36 语言) | 84.4% | **95.0%** |
| 向量维度 | 1024 | 768（计算更快） |
| 语言数量 | 93 | 109 |
| 维护状态 | fairseq 已停滞 | Google 持续维护 |
| 安装方式 | `laser_encoders` + fairseq hack | `pip install sentence-transformers` |

#### 4.6.2 实现

```python
class Embedder:
    """跨语言句子嵌入"""

    def __init__(self, model_name: str = 'sentence-transformers/LaBSE'):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, sentences: list[str], batch_size: int = 64) -> np.ndarray:
        """
        编码句子列表为向量矩阵。

        Returns:
            np.ndarray, shape (N, dim), dtype float32, L2 归一化
        """
        return self.model.encode(
            sentences,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(sentences) > 100,
        ).astype(np.float32)
```

vecalign 核心对向量维度**无硬性要求**——`dp_utils.py` 在读取 embedding 时自动推断维度（代码第 64-68 行），仅在维度不等于 1024 时打印 warning，不影响功能。

### 4.7 对齐器抽象基类 — `align/base.py`

```python
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
```

### 4.8 Vecalign 适配器 — `align/vecalign_adapter.py`

**目标**：将 vecalign 从 CLI 工具改造为可在内存中调用的 Python 函数，**不修改 vecalign 源码**。

#### 4.8.1 vecalign 原始数据流（文件 I/O）

```
1. 输入文本文件 → 每行一个句子
2. overlap.py → 生成 overlap 文本文件
3. 外部编码 → LASER → 生成 embedding 二进制文件
4. vecalign.py → 读取文件 → DP 对齐 → stdout 输出
```

#### 4.8.2 改造后的数据流（内存）

```
1. list[str] 输入
2. 内存中调用 yield_overlaps() 生成 overlap 文本
3. 合并所有文本 → Embedder.encode() → ndarray
4. 构造 sent2line dict + embedding 矩阵
5. 调用 make_doc_embedding() → 文档向量
6. 调用 dp_utils.vecalign() → 对齐路径
```

```python
class VecalignAdapter(BaseAligner):
    def __init__(self, embedder: Embedder, max_align_size: int = 4):
        self.embedder = embedder
        self.max_align_size = max_align_size

    def align(self, src_texts: list[str], tgt_texts: list[str]):
        from bookalign.vendor.vecalign.dp_utils import (
            yield_overlaps, make_doc_embedding, vecalign as run_vecalign,
            make_norm1, preprocess_line,
        )

        # 1. 生成 overlap 文本
        src_lines = list(yield_overlaps(src_texts, self.max_align_size))
        tgt_lines = list(yield_overlaps(tgt_texts, self.max_align_size))
        all_lines = src_lines + tgt_lines

        # 2. 批量编码
        all_embeddings = self.embedder.encode(all_lines)

        # 3. 构造 sent2line 映射（绕过 read_in_embeddings 的文件 I/O）
        sent2line = {}
        for i, line in enumerate(all_lines):
            processed = preprocess_line(line)
            if processed not in sent2line:  # 去重
                sent2line[processed] = i

        # 4. 构建文档嵌入矩阵
        src_vecs = make_doc_embedding(
            sent2line, all_embeddings, src_texts, self.max_align_size
        )
        tgt_vecs = make_doc_embedding(
            sent2line, all_embeddings, tgt_texts, self.max_align_size
        )

        # 5. 归一化
        src_vecs = make_norm1(src_vecs)
        tgt_vecs = make_norm1(tgt_vecs)

        # 6. 执行对齐
        final_alignment_types = make_alignment_types(self.max_align_size)
        stack = run_vecalign(
            src_vecs, tgt_vecs,
            final_alignment_types,
            del_percentile_frac=0.2,
            max_size_full_dp=300,
            costs_sample_size=20000,
            num_samps_for_norm=100,
            search_buffer_size=5,
        )

        # 7. 转换为统一输出格式
        return self._convert_stack(stack, src_texts, tgt_texts)
```

**关键改造点总结**：
- `dp_utils.read_in_embeddings()` → 跳过，直接构造 `sent2line` dict + ndarray
- `dp_utils.make_doc_embedding()` → 原样调用
- `dp_utils.vecalign()` → 原样调用
- vecalign 源码本身**零改动**

### 4.9 Bertalign 适配器 — `align/bertalign_adapter.py`

Bertalign 是专为文学翻译对齐设计的 Python 库（2023 年发表，Oxford Academic），在中英文学文本 F1 上优于 vecalign。

#### 4.9.1 Bertalign 算法核心

**两步动态规划**：
1. **锚点发现**：用 sentence-transformers 编码，找到每个源句的 top-k 最相似目标句，确定 1-to-1 锚点
2. **完整对齐**：以锚点为约束，在窗口内用 DP 搜索所有 1-to-many、many-to-1、many-to-many 对齐

#### 4.9.2 与 vecalign 的对比

| 维度 | vecalign | Bertalign |
|------|----------|-----------|
| 算法 | 近似 DTW（线性时空复杂度）| 完整 DP（更高精度）|
| 精度 (Bible) | P=0.957, R=0.958 | P=0.974, R=0.973 |
| 多对多支持 | 通过 overlap 机制间接支持 | 原生设计支持 |
| 预处理 | 需要外部 embedding + overlap 文件 | 内置 embedding 和切分 |
| API 设计 | CLI 工具 | Python 库（可直接 import）|
| 文学文本适配 | 通用对齐 | 专为文学翻译设计 |

#### 4.9.3 实现

```python
class BertalignAdapter(BaseAligner):
    def __init__(
        self,
        model_name: str = 'sentence-transformers/LaBSE',
        max_align: int = 5,
        top_k: int = 3,
        win: int = 5,
        skip: float = -0.1,
    ):
        self.model_name = model_name
        self.max_align = max_align
        self.top_k = top_k
        self.win = win
        self.skip = skip

    def align(self, src_texts: list[str], tgt_texts: list[str]):
        from bertalign import Bertalign

        # is_split=True 跳过 bertalign 内置的句子切分
        # 因为我们已经在 extractor 中完成了切分
        aligner = Bertalign(
            '\n'.join(src_texts),
            '\n'.join(tgt_texts),
            is_split=True,
            max_align=self.max_align,
            top_k=self.top_k,
            win=self.win,
            skip=self.skip,
        )
        aligner.align_sents()

        return self._convert_result(aligner.result, src_texts, tgt_texts)

    def _convert_result(self, result, src_texts, tgt_texts):
        """将 bertalign 结果转为统一格式 [(src_idx, tgt_idx, score)]"""
        alignments = []
        for src_idxs, tgt_idxs in result:
            # bertalign 不输出 score，用 1.0 作为默认
            alignments.append((list(src_idxs), list(tgt_idxs), 1.0))
        return alignments
```

**安装**：
```bash
pip install git+https://github.com/bfsujason/bertalign.git
```

**依赖**：sentence-transformers, numba, faiss-cpu（不需 GPU 版）

**注意事项**：
- Bertalign 内部自行加载 embedding 模型，与我们的 `Embedder` 独立
- MVP 阶段先接受这一冗余，后续可 fork 修改其模型加载逻辑以共享实例
- `is_split=True` 是关键参数——告诉 bertalign 输入已经切分好，不需要再切

### 4.10 对齐调度入口 — `align/aligner.py`

```python
def align_book(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    engine: str = 'vecalign',       # 'vecalign' | 'bertalign'
    embedder: Embedder | None = None,
) -> AlignmentResult:
    """
    对齐两本书的 Segment 列表。

    策略：
    1. 如果两书章节数一致，按章节逐段对齐（大幅减小 DP 矩阵）
    2. 如果章节数不一致，整书对齐
    """
```

**按章节分组对齐**：

文学作品翻译通常保留原书章节结构，两书章节数一致的概率很高。逐章对齐的好处：
- 将 O(N²) 的 DP 问题分解为多个小的 O(nᵢ²) 问题
- 减少跨章节错误对齐的可能
- 支持并行化处理

回退策略：章节数不一致时，先做**章节级粗对齐**（将章节作为大段落对齐），再在配对的章节内做细粒度对齐。

### 4.11 双语 EPUB 重建 — `epub/builder.py`

```python
def build_bilingual_epub(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
) -> None:
    """
    基于对齐结果，以原书为骨架构建双语 EPUB。

    骨架逻辑：
    1. 复制原书元数据、目录结构、CSS、图片等非内容资源
    2. 对每个章节的 XHTML 进行内容替换
    3. 注入双语 CSS
    4. 写出新 EPUB
    """
```

#### 4.11.1 段落级渲染模板

```html
<div class="bilingual-pair">
  <div class="source" lang="ja">
    <!-- 保留原文 HTML，含 ruby/em 等样式标签 -->
    <p>幼時から父は、私によく、<ruby>金閣<rt>きんかく</rt></ruby>のことを語った。</p>
  </div>
  <div class="translation" lang="zh">
    <p>从幼年起，父亲就常常对我讲述金阁的事。</p>
  </div>
</div>
```

#### 4.11.2 句子级渲染模板

```html
<div class="sentence-pair">
  <p class="src-sent" lang="ja">幼時から父は、私によく、金閣のことを語った。</p>
  <p class="tgt-sent" lang="zh">从幼年起，父亲就常常对我讲述金阁的事。</p>
</div>
<div class="sentence-pair">
  <p class="src-sent" lang="ja">父の故郷は……</p>
  <p class="tgt-sent" lang="zh">父亲的故乡是……</p>
</div>
<!-- 原始段落边界：加大间距 -->
<div class="para-break"></div>
```

#### 4.11.3 注入 CSS

```css
.bilingual-pair { margin-bottom: 1.5em; }
.translation, .tgt-sent {
    color: #555;
    font-size: 0.9em;
    margin-left: 1em;
    border-left: 2px solid #ddd;
    padding-left: 0.8em;
}
.para-break { margin-bottom: 2em; }
.sentence-pair { margin-bottom: 0.5em; }
```

---

## 5. 依赖管理

### 5.1 pyproject.toml 更新

```toml
[project]
name = "bookalign"
version = "0.1.0"
description = "Align original and translated EPUBs into bilingual e-books"
requires-python = ">=3.12"
dependencies = [
    "ebooklib>=0.20",
    "lxml>=5.0",
    "sentence-transformers>=3.0",
    "pysbd>=0.3",
    "numpy>=1.26",
    "click>=8.0",
]

[project.optional-dependencies]
bertalign = [
    "bertalign @ git+https://github.com/bfsujason/bertalign.git",
]
vecalign = [
    "cython>=3.0",
]
dev = [
    "pytest>=8.0",
]

[project.scripts]
bookalign = "bookalign.cli:main"
```

### 5.2 依赖说明

| 包 | 用途 | 必需 |
|----|------|------|
| ebooklib | EPUB 读写 | ✅ |
| lxml | XHTML 解析 | ✅ |
| sentence-transformers | LaBSE 模型加载 | ✅ |
| pysbd | 句子切分 | ✅ |
| numpy | 向量运算 | ✅ |
| click | CLI | ✅ |
| cython | vecalign dp_core 编译 | 仅 vecalign 引擎 |
| bertalign | 对齐引擎备选 | 可选 |

---

## 6. CLI 设计 — `cli.py`

```python
@click.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, type=click.Path())
@click.option('--granularity', type=click.Choice(['paragraph', 'sentence']),
              default='paragraph')
@click.option('--engine', type=click.Choice(['vecalign', 'bertalign']),
              default='vecalign')
@click.option('--src-lang', default=None, help='源语言代码，如 ja/zh/en')
@click.option('--tgt-lang', default=None, help='目标语言代码')
def main(source, target, output, granularity, engine, src_lang, tgt_lang):
    """将原版 EPUB 和译版 EPUB 对齐，输出双语 EPUB。"""
```

用法：
```bash
# 段落级对齐（默认）
bookalign books/kinkaku.epub books/kinkaku_zh.epub -o bilingual.epub

# 句子级对齐 + bertalign 引擎
bookalign books/kinkaku.epub books/kinkaku_zh.epub -o bilingual.epub \
    --granularity sentence --engine bertalign

# 指定语言
bookalign src.epub tgt.epub -o out.epub --src-lang ja --tgt-lang en
```

---

## 7. 分阶段开发路线

### Phase 1 — MVP：段落级对齐 + vecalign

**目标**：跑通完整流水线，输出段落级双语 EPUB。

| 步骤 | 模块 | 工作内容 | 预估代码量 |
|------|------|---------|-----------|
| 1 | `models/types.py` | 定义 Segment / AlignedPair / AlignmentResult | ~50 行 |
| 2 | `epub/reader.py` | 迁移 read_book.py + 元数据提取 | ~40 行 |
| 3 | `epub/tag_filters.py` | 标签过滤规则 | ~60 行 |
| 4 | `epub/extractor.py` | XHTML → 段落 Segment（含标签过滤） | ~150 行 |
| 5 | `align/embedder.py` | LaBSE 封装 | ~30 行 |
| 6 | `vendor/vecalign/` | 移动现有 vecalign 代码 + `__init__.py` | 文件移动 |
| 7 | `align/base.py` | 对齐器基类 | ~20 行 |
| 8 | `align/vecalign_adapter.py` | vecalign 内存调用适配 | ~120 行 |
| 9 | `align/aligner.py` | 章节分组 + 对齐调度 | ~80 行 |
| 10 | `epub/builder.py` | 双语 EPUB 段落级输出 | ~150 行 |
| 11 | `cli.py` | 基础 CLI | ~50 行 |
| 12 | `pipeline.py` | 串联所有模块 | ~60 行 |

**验收标准**：
- 用 `kinkaku.epub`（日文金閣寺）+ 中文/英文译本生成双语 EPUB
- 输出文件可在 Calibre / Apple Books 中正常打开
- 段落对齐基本正确（抽查 20 段，准确率 > 80%）

### Phase 2 — 句子级对齐

| 步骤 | 模块 | 工作内容 |
|------|------|---------|
| 13 | `epub/sentence_splitter.py` | SentenceSplitter 实现（ja/zh/en） |
| 14 | `epub/extractor.py` | 增加句子切分模式 + 句子-Span 映射 |
| 15 | `epub/builder.py` | 句子级渲染模板 |
| 16 | 测试 | 验证句子切分质量 + 句子级对齐效果 |

### Phase 3 — Bertalign 引擎集成

| 步骤 | 模块 | 工作内容 |
|------|------|---------|
| 17 | `align/bertalign_adapter.py` | Bertalign 适配器实现 |
| 18 | `cli.py` | 增加 `--engine bertalign` 支持 |
| 19 | 测试 | 对比 vecalign vs bertalign 在文学文本上的表现 |

### Phase 4 — 优化与扩展

| 方向 | 内容 |
|------|------|
| 章节自动配对 | 章节数不一致时，先做章节级粗对齐 |
| 对齐质量 | 低置信度结果的人工审核接口 |
| 更多语言 | es/fr/de 等句子切分规则扩展 |
| CFI 精确定位 | 句子级 CFI 标注（整合 v2 能力） |
| 样式深度保留 | 字体、图片、复杂 CSS 的完整保留 |
| 用户界面 | Web UI (Gradio/Streamlit) 或 TUI |

---

## 8. 测试策略

### 8.1 单元测试

| 测试文件 | 覆盖模块 | 测试内容 |
|---------|---------|---------|
| `test_extractor.py` | extractor + tag_filters | 用 `books/0004.xhtml` 验证：ruby 保留主体 / rt 被过滤 / span.super 被跳过 / 空段落被忽略 |
| `test_splitter.py` | sentence_splitter | 日文、中文、英文、西班牙文各 5-10 条测试用例 |
| `test_aligner.py` | vecalign_adapter / bertalign_adapter | 5-10 句的简短双语文本，验证对齐正确性 |
| `test_builder.py` | builder | 验证输出 EPUB 的结构完整性（CSS 注入、章节存在、元数据正确） |

### 8.2 端到端测试

```bash
# 生成双语 EPUB 并验证可打开
bookalign books/kinkaku.epub books/kinkaku_zh.epub -o /tmp/test_bilingual.epub
python -c "import ebooklib; ebooklib.epub.read_epub('/tmp/test_bilingual.epub')"
```

### 8.3 对齐质量评估

手动抽检 + 可选的自动评估：
- 随机抽取 30 对段落，人工判断对齐是否正确
- 如果有 gold standard 对齐数据，可用 `vecalign/score.py` 计算 P/R/F1

---

## 9. 已知风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 两书章节结构差异大 | 逐章对齐失效 | 回退到全书对齐；Phase 4 实现章节自动配对 |
| 译文大幅删减/意译 | 句子级对齐偏差 | 使用段落级作为保底；Bertalign 对意译更鲁棒 |
| vecalign Cython 编译问题 | dp_core.pyx 无法编译 | 提供纯 Python fallback（性能降低但可用） |
| LaBSE 模型首次下载慢 | 首次运行耗时 | 支持离线模型路径配置 |
| Bertalign faiss 安装问题 | 可选引擎不可用 | 作为 optional dependency，vecalign 作为默认 |
