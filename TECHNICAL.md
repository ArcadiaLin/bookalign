# BookAlign 技术说明

## 1. 文档目的

本文档用于说明 BookAlign 当前实现中的：

- 模块职责
- 核心数据结构
- 公开接口
- 关键算法与启发式
- builder 工作方式
- 端到端调用流程

它面向后续开发、重构和提交审查，而不是用户级介绍。

## 2. 核心概念

### 2.1 `Segment`

`Segment` 是整个系统的基础工作单元。

定义位于 `bookalign/models/types.py`：

```python
@dataclass
class Segment:
    text: str
    cfi: str
    chapter_idx: int
    paragraph_idx: int
    sentence_idx: int | None
    paragraph_cfi: str = ''
    text_start: int | None = None
    text_end: int | None = None
    raw_html: str = ''
    element_xpath: str = ''
    spans: list[TextSpan] = field(default_factory=list)
```

字段语义：

- `text`: 对齐和显示使用的规范化文本
- `cfi`: 当前 `Segment` 的范围锚点；句子级时是句子范围 CFI
- `chapter_idx`: 所属 spine 文档索引
- `paragraph_idx`: 在该章节中的段落序号
- `sentence_idx`: 在该段中的句子序号；段落级时为 `None`
- `paragraph_cfi`: 所属段落的范围锚点；source-layout 回写主锚点
- `text_start` / `text_end`: 句子在段落规范化文本中的位置
- `raw_html`: 源块原始 HTML 片段
- `element_xpath`: 调试和审阅用 XPath
- `spans`: `TextSpan` 列表，用于句位映射和 CFI 生成

### 2.2 `TextSpan`

`TextSpan` 表示“一个可见文本片段及其来源位置”：

```python
@dataclass
class TextSpan:
    text: str
    xpath: str
    text_node_index: int
    char_offset: int
    source_kind: str = 'text'
    cfi_text_node_index: int | None = None
    cfi_exact: bool = False
```

用途：

- 由 extractor 从 DOM 收集得到
- 为段落文本拼接提供材料
- 为句子分段后重新映射到原 DOM 提供桥梁

### 2.3 `AlignedPair` 与 `AlignmentResult`

```python
@dataclass
class AlignedPair:
    source: list[Segment]
    target: list[Segment]
    score: float

@dataclass
class AlignmentResult:
    pairs: list[AlignedPair]
    source_lang: str
    target_lang: str
    granularity: str
```

说明：

- `source` / `target` 都是列表，以支持 1:n / n:1 / 0:n / n:0 bead
- `score` 当前为适配器输出的工程分值，不是严格概率

## 3. 模块结构

### 3.1 `bookalign/epub/reader.py`

职责：

- 读取 EPUB
- 提取元数据
- 返回可读 spine 文档

公开接口：

```python
read_epub(path: str | Path) -> epub.EpubBook
get_metadata(book: epub.EpubBook) -> dict
get_spine_documents(book: epub.EpubBook) -> list[tuple[int, epub.EpubHtml]]
```

设计说明：

- `get_spine_documents()` 是 extractor、builder 和测试共同依赖的统一入口
- 所有后续索引编号默认以这里返回的 spine 顺序为准

### 3.2 `bookalign/epub/tag_filters.py`

职责：

- 定义元素抽取策略
- 提供标签与属性层面的启发式控制

关键类型：

- `ExtractAction`
- `ElementPolicy`
- `TagFilterConfig`

当前常见动作：

- `SKIP_ENTIRE`
- `KEEP_NORMAL`
- `KEEP_CHILDREN_ONLY`
- `KEEP_DIRECT_TEXT_ONLY`
- `INLINE_BREAK`
- `BLOCK_BREAK`
- `STRUCTURAL_CONTAINER`

典型规则：

- `ruby` 保留正文，不保留 `rt/rp`
- `a.noteref` / footnote 引用跳过
- `aside[epub:type=footnote]` 跳过
- `br` 作为轻量断行信号
- `section/header/footer/nav` 等结构容器不直接作为正文段落

### 3.3 `bookalign/epub/sentence_splitter.py`

职责：

- 针对语言做句子切分
- 执行规范化文本处理

公开接口：

```python
SentenceSplitter(language: str = 'ja')
```

当前语言：

- `ja`
- `zh`
- `en`
- `es`

设计说明：

- CJK 语言主要走标点规则和后处理
- 英西文优先利用 `pysbd`
- 对话引号、闭合引号、`br` 密集段落会做附加收敛

### 3.4 `bookalign/epub/cfi.py`

职责：

- 解析和生成 EPUB CFI
- 将 CFI 解析回 DOM/text 节点
- 做 range 文本回提

核心接口：

```python
parse_item_xml(item: epub.EpubItem)
resolve_cfi(cfi_str: str, book: epub.EpubBook, _root=None) -> dict | None
generate_cfi_for_text_range(book, item, element, start_tni, start_off, end_tni, end_off, _root=None) -> str | None
extract_range_text(range_result: dict) -> str | None
```

实现原则：

- 生产路径以 CFI 为主锚点
- `_root` 参数允许 builder/extractor 在已解析 DOM 上复用解析结果
- `extract_text_from_cfi()` 在 extractor 层与正文定义保持一致，用于 roundtrip 测试

### 3.5 `bookalign/epub/extractor.py`

职责：

- 识别块级正文候选
- 从块级节点收集 `TextSpan`
- 构造段落级和句子级 `Segment`
- 用同一套规则支持回提验证

公开接口：

```python
extract_segments(
    book: epub.EpubBook,
    doc: epub.EpubHtml,
    chapter_idx: int,
    config: TagFilterConfig | None = None,
    splitter: SentenceSplitter | None = None,
) -> list[Segment]

extract_text_from_cfi(
    book: epub.EpubBook,
    cfi: str,
    config: TagFilterConfig | None = None,
) -> str

collect_debug_spans(element, config: TagFilterConfig | None = None) -> list[DebugSpan]
```

工作流程：

```text
遍历文档节点
-> 找到 BLOCK_BREAK 且非 STRUCTURAL_CONTAINER 的块
-> 收集可见文本 span
-> trim 空白与前后噪声
-> 生成 paragraph range CFI
-> 做段落启发式过滤
-> 若未传 splitter: 输出 paragraph Segment
-> 若传入 splitter: 句子切分并映射回 sentence Segment
```

关键点：

- 段落和句子 `Segment` 共用同一套 `TextSpan` 基础
- 句子 `Segment.paragraph_cfi` 始终指向所属段落
- `text_start` / `text_end` 记录句子在段落文本内的位置

### 3.6 `bookalign/align/base.py`

职责：

- 定义对齐引擎统一接口

```python
class BaseAligner(ABC):
    @abstractmethod
    def align(
        self,
        src_texts: list[str],
        tgt_texts: list[str],
    ) -> list[tuple[list[int], list[int], float]]:
        ...
```

约定：

- 返回值是 bead 级索引映射
- 允许一侧为空列表，用于插入/删除对齐

### 3.7 `bookalign/align/bertalign_adapter.py`

职责：

- 将 vendored `bertalign` 适配到项目接口

公开接口：

```python
BertalignAdapter(
    *,
    model_name: str = 'sentence-transformers/LaBSE',
    max_align: int = 5,
    top_k: int = 3,
    win: int = 5,
    skip: float = -0.1,
    margin: bool = True,
    len_penalty: bool = True,
    src_lang: str | None = None,
    tgt_lang: str | None = None,
    default_score: float = 1.0,
)
```

实现细节：

- 运行时动态把 `bookalign/vendor/bertalign` 加到 `sys.path`
- 调用 `vendor.configure_model(model_name)`
- 以已经分好句的文本列表作为输入，设置 `is_split=True`
- 将 vendor 结果统一封装成项目 bead 格式

### 3.8 `bookalign/align/aligner.py`

职责：

- 把 `BaseAligner` 的 bead 结果映射回 `Segment`
- 生成 `AlignedPair`

关键接口：

```python
align_segments(
    src_segments: list[Segment],
    tgt_segments: list[Segment],
    *,
    source_lang: str,
    target_lang: str,
    granularity: str,
    aligner: BaseAligner | None = None,
) -> AlignmentResult
```

### 3.9 `bookalign/pipeline.py`

职责：

- 端到端编排
- 章节抽取
- 章节匹配
- 逐章句子对齐
- builder 调度

核心类型：

```python
@dataclass
class ExtractedChapter:
    spine_idx: int
    doc: epub.EpubHtml
    segments: list[Segment]

@dataclass
class ChapterMatch:
    source_chapter: ExtractedChapter
    target_chapter: ExtractedChapter
    score: float
```

公开接口：

```python
extract_sentence_chapters(book, *, language: str) -> list[ExtractedChapter]
match_extracted_chapters(source_chapters, target_chapters, *, chapter_match_mode: str = 'structured') -> list[ChapterMatch]
align_extracted_chapters(source_chapters, target_chapters, *, source_lang: str, target_lang: str, chapter_match_mode: str = 'structured', aligner: BaseAligner | None = None) -> AlignmentResult
align_books(source_book, target_book, *, source_lang: str, target_lang: str, chapter_match_mode: str = 'structured', aligner: BaseAligner | None = None) -> AlignmentResult
run_bilingual_epub_pipeline(*, source_epub_path, target_epub_path, output_path, source_lang='ja', target_lang='zh', builder_mode='simple', chapter_match_mode='structured', layout_direction='horizontal', emit_translation_metadata=False, aligner=None) -> AlignmentResult
```

#### 章节匹配原理

`match_extracted_chapters()` 使用顺序 DP，在 source/target 章节序列上寻找最小代价路径。

代价组成：

- `count_cost`: 句子数量比例差异
- `paratext_cost`: source/target 是否同为附文
- `marker_cost`: 章节名中的编号是否一致
- `position_cost`: 在整本书中的相对位置差异

#### `structured` vs `raw`

`structured`：

- 使用 paratext 偏置
- source/target 一侧看起来像目录/版权/后记时，跳过成本更低
- 适合真实生产路径

`raw`：

- 不启用 paratext-aware skip bias
- 保留原始顺序与长度约束
- 适合做对照实验，观察“不过滤直接对齐”的结果

### 3.10 `bookalign/epub/builder.py`

职责：

- 根据 `AlignmentResult` 输出 EPUB
- 提供 `simple` 与 `source_layout` 两种构建策略

公开接口：

```python
build_bilingual_epub(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
) -> None

build_bilingual_epub_on_source_layout(
    alignment: AlignmentResult,
    source_book: epub.EpubBook,
    target_book: epub.EpubBook,
    output_path: Path,
    *,
    layout_direction: str = 'horizontal',
    emit_translation_metadata: bool = False,
) -> None
```

#### `simple` builder 原理

- 按章节归并 `AlignedPair`
- 新建 XHTML 页面
- 每个段落块里顺序写入 source/target 句对
- 对 source-only / target-only pair 使用缺失占位

适合：

- 评估对齐结果
- 查对句对边界
- 与 source-layout 输出做并排比较

#### `source_layout` builder 原理

工作流程：

```text
遍历 alignment pairs
-> 按 source (chapter_idx, paragraph_idx, paragraph_cfi) 聚合同段译文
-> 找到 source XHTML 对应段落
-> 在该段后注入 plain <p> 译文段
-> 插入一个空白分隔段
-> 保留原书 head/title/stylesheet
-> 追加 bookalign 覆盖 CSS
-> 写出新的 EPUB
```

关键实现点：

- 使用 `paragraph_cfi` 锚定段落，而不是用最后一句 `cfi`
- 默认不输出 `class/lang/data-bookalign-*` 调试属性
- `emit_translation_metadata=True` 时才输出调试元数据
- 输出 XHTML 使用 `pretty_print=True`，便于直接审查

#### 为什么要保留原始 `<head>`

如果只重建 `<body>`，会丢失：

- 原始 `<title>`
- 原书 stylesheet link
- 原文档语言声明
- 某些阅读器依赖的 meta 信息

因此 builder 会优先解析原始 `doc.content`，并回填这些头部信息。

#### 横排兼容策略

当 `layout_direction='horizontal'` 时：

- 覆盖 CSS 为 `horizontal-tb`
- 强制左对齐
- 取消默认首行缩进
- 输出书方向设为 `ltr`

这样既修正文档方向，也修正阅读器分页语义。

### 3.11 `bookalign/epub/debug_report.py`

职责：

- 从真实 EPUB 中抽样
- 输出 Markdown 审阅报告
- 用于人工检查 extractor 质量

CLI 接口：

```bash
uv run python -m bookalign.epub.debug_report \
  --book kinkaku.epub \
  --language ja \
  --granularity sentence \
  --test-type mixed \
  --debug \
  --output tests/artifacts/epub_debug_report.md
```

关键参数：

- `--book`: 文件名、glob 或绝对路径
- `--sample-count`: 抽样数量
- `--test-type`: `normal|complex|ruby|footnote|mixed`
- `--granularity`: `paragraph|sentence`
- `--debug`: 是否附加 debug spans

## 4. 端到端调用流程

### 4.1 命令行

```bash
uv run bookalign SOURCE.epub TARGET.epub OUTPUT.epub \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --chapter-match-mode structured \
  --layout-direction horizontal
```

执行顺序：

1. `cli.py` 解析参数
2. `run_bilingual_epub_pipeline()` 读取两本书
3. `align_books()` 对两侧做句子抽取
4. `match_extracted_chapters()` 找到章节映射
5. `align_segments()` 逐章调用 `BertalignAdapter`
6. 根据 `builder_mode` 调用对应 builder
7. 写出 EPUB

### 4.2 编程调用

最常见入口：

```python
from pathlib import Path
from bookalign.pipeline import run_bilingual_epub_pipeline

alignment = run_bilingual_epub_pipeline(
    source_epub_path=Path("source.epub"),
    target_epub_path=Path("target.epub"),
    output_path=Path("out.epub"),
    source_lang="ja",
    target_lang="zh",
    builder_mode="source_layout",
    chapter_match_mode="structured",
    layout_direction="horizontal",
)
```

若只想拿到对齐结果：

```python
from bookalign.epub.reader import read_epub
from bookalign.pipeline import align_books

source_book = read_epub("source.epub")
target_book = read_epub("target.epub")
result = align_books(
    source_book,
    target_book,
    source_lang="ja",
    target_lang="zh",
)
```

## 5. 测试结构

当前主要测试文件：

- `tests/test_splitter.py`
- `tests/test_extractor.py`
- `tests/test_aligner.py`
- `tests/test_pipeline.py`
- `tests/test_builder.py`

覆盖重点：

- 分句边界
- CFI roundtrip
- `paragraph_cfi` 继承
- 章节匹配 structured/raw 行为
- simple/source-layout builder 行为
- 《金阁寺》真实书籍集成路径

## 6. 真实书籍验证策略

当前以《金阁寺》为主要样本，原因是：

- source/target 都可用
- 原书与译本前后附文不完全对齐
- 日文竖排和中文横排差异明显
- 能有效暴露 source-layout builder 的兼容性问题

这本书已经用于验证：

- 章节匹配
- Bertalign 实跑
- simple builder
- source-layout builder
- 阅读方向与分页修复

## 7. 当前限制与推荐重构边界

### 7.1 不建议当前直接动 extractor 主线的部分

- block 识别规则的大范围重写
- `TextSpan` 到句位映射逻辑的推翻
- CFI 生成方式的大改

原因：

- 这些已经是现有 pipeline 的稳定基础
- builder 和对齐层都依赖它们

### 7.2 当前适合继续演进的部分

- 章节匹配代价函数
- builder 的注入策略和样式兼容
- 对齐质量的评分和审阅工具
- 更多真实书籍回归

## 8. 提交卫生约定

- `tests/artifacts/` 默认视为生成目录
- 当前仅提交 `tests/artifacts/batch_reader_reports/`
- 真实运行生成的 EPUB、截图、一次性调试报告不纳入常规提交
- 根目录过时说明文档已合并到本文档，不再保留分散 extraction 说明
