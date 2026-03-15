# BookAlign 设计说明

## 1. 项目目标

BookAlign 当前的目标不是一次性完成“语义完美的双语重建”，而是先把底层抽取链路做稳定：

1. 从不同来源 EPUB 中抽取可对齐的段落或句子文本。
2. 尽量保留可回溯到原书结构的定位信息。
3. 为后续对齐、重建、语义筛选提供干净且一致的输入。

当前阶段最重要的不是 `aligner` 或 `builder`，而是：

1. `reader`
2. `extractor`
3. `tag_filters`
4. `sentence_splitter`
5. `cfi`

如果抽取边界不稳定，后续所有语义任务都会被噪音和结构偏差放大。

## 2. 当前设计原则

### 2.1 抽取边界

这一层只做“规则驱动的启发式抽取”，不做语义级正文理解。

也就是说：

1. 目标是尽量从结构相对健康的 EPUB 中抽出可对齐句子。
2. 不要求在这一层完美识别什么是“真正正文”。
3. 对明显不健康的块，只做规则层面的降噪和过滤。
4. 更高层的正文甄别、语义判断和对齐修正，交给后续模块。

### 2.2 主定位方式

当前主流程以 `CFI` 为核心定位方式。

1. `Segment.cfi` 是运行时主锚点。
2. `XPath` 只保留给调试、测试和人工排查。
3. 句子级 `Segment` 不是重新扫 DOM，而是从段落级 `TextSpan` 切片得到。

### 2.3 规则 + 策略

`tag_filters` 已从“skip 规则集合”升级为“规则 + 动作”模型。

核心结构：

1. `ElementPolicy`
2. `ExtractAction`
3. `match_element_policy()`
4. `get_extract_action()`

这意味着当前系统不仅能表达“跳过什么”，还可以表达“如何抽取这个节点”。

## 3. 当前目录结构

当前建议保留的主目录如下：

```text
bookalign/
├── __init__.py
├── cli.py
├── pipeline.py
├── models/
│   ├── __init__.py
│   └── types.py
├── epub/
│   ├── __init__.py
│   ├── reader.py
│   ├── extractor.py
│   ├── cfi.py
│   ├── sentence_splitter.py
│   ├── tag_filters.py
│   ├── debug_report.py
│   └── builder.py
├── align/
│   ├── __init__.py
│   ├── aligner.py
│   ├── base.py
│   ├── bertalign_adapter.py
│   ├── embedder.py
│   └── vecalign_adapter.py
└── vendor/
    ├── __init__.py
    ├── bertalign/
    └── vecalign/
```

测试与文档：

```text
tests/
├── test_extractor.py
├── test_splitter.py
├── test_aligner.py
├── test_builder.py
└── artifacts/

DESIGN.md
STATUS.md
EPUB_EXTRACTION.md
EXTRACTION_REFACTOR.md
```

## 4. 核心数据模型

文件：`bookalign/models/types.py`

### 4.1 Segment

`Segment` 是当前生产路径的核心抽象。

关键字段：

1. `text`
2. `cfi`
3. `chapter_idx`
4. `paragraph_idx`
5. `sentence_idx`
6. `raw_html`

补充字段：

1. `element_xpath`
2. `spans`

其中：

1. `text` 用于对齐
2. `cfi` 用于回提与重建
3. `raw_html` 用于保留原块内容和后续样式参考
4. `chapter_idx / paragraph_idx` 用于稳定结构编号
5. `element_xpath / spans` 主要用于调试和测试

### 4.2 TextSpan

`TextSpan` 表示一段“可读文本片段”和它在 DOM / CFI 中的来源关系。

它承担两个作用：

1. 段落可读文本的构建材料
2. 句子级切片和句级 CFI 生成的桥梁

### 4.3 DebugSpan

`DebugSpan` 只服务于测试层和审阅层，不属于生产主模型。

当前包含：

1. `xpath`
2. `tag`
3. `text_preview`
4. `action`
5. `policy_name`

## 5. 模块职责

### 5.1 reader

文件：`bookalign/epub/reader.py`

职责：

1. 读取 EPUB
2. 按 spine 获取 XHTML 文档
3. 提取基础元数据

### 5.2 tag_filters

文件：`bookalign/epub/tag_filters.py`

职责：

1. 为元素匹配规则
2. 给出抽取动作
3. 保持 extractor 不直接堆满标签判断

当前核心动作：

1. `SKIP_ENTIRE`
2. `KEEP_NORMAL`
3. `KEEP_CHILDREN_ONLY`
4. `KEEP_DIRECT_TEXT_ONLY`
5. `INLINE_BREAK`
6. `BLOCK_BREAK`
7. `STRUCTURAL_CONTAINER`

典型内建策略：

1. `ruby -> KEEP_CHILDREN_ONLY`
2. `rt / rp -> SKIP_ENTIRE`
3. `br -> INLINE_BREAK`
4. `span.super -> SKIP_ENTIRE`
5. `a.noteref / a[epub:type=noteref] -> SKIP_ENTIRE`
6. `aside[epub:type=footnote] -> SKIP_ENTIRE`
7. `section/article/header/footer -> STRUCTURAL_CONTAINER`

除此之外，`TagFilterConfig` 还承载块级启发式过滤配置，例如：

1. 明显 license / Gutenberg 噪音模式
2. 目录 / heading / metadata 候选模式
3. 数字页码 / 分隔符行模式

### 5.3 extractor

文件：`bookalign/epub/extractor.py`

这是当前项目的核心实现。

它负责：

1. 找出块级候选节点
2. 按策略提取可读 `TextSpan`
3. 做空白规范化与噪音行清理
4. 生成段落级 `Segment`
5. 在需要时切成句子级 `Segment`
6. 为段落和句子都生成 `range CFI`

当前 extractor 的关键设计点：

1. 节点行为由 `ExtractAction` 决定，而不是零散 `if tag == ...`
2. `extract_text_from_cfi()` 与主 extractor 共用同一套正文定义
3. 句子级映射基于段落 `spans` 切片，而不是重新扫描 DOM

### 5.4 sentence_splitter

文件：`bookalign/epub/sentence_splitter.py`

当前支持：

1. `ja`
2. `zh`
3. `en`
4. `es`

当前策略：

1. `ja/zh` 采用 CJK 标点规则切分，并处理尾部引号/括号
2. `en/es` 基于 `pysbd`
3. 对英西文对白做后处理，尽量把 quote + narration 合并回自然句子

已明确的当前边界：

1. 不专门处理诗行
2. `br` 很多的段落会做 line-aware 启发式切分，但它仍然是面向“可对齐句子”的折中方案，不是诗歌排版保真方案
3. 复杂对白、长引号、文学化省略号仍会有误差

### 5.5 cfi

文件：`bookalign/epub/cfi.py`

职责：

1. 解析 EPUB CFI
2. 解析 range CFI
3. 从已知 DOM 节点和 offset 生成 CFI
4. 支持文本范围的回提

当前定位结论：

1. 主流程依赖 `CFI`
2. `XPath` 不作为运行时核心定位手段

### 5.6 debug_report

文件：`bookalign/epub/debug_report.py`

职责：

1. 针对某本书按条件抽样
2. 输出 Markdown 审阅报告
3. 展示 `raw_html`、`text`、句子结果、debug spans、CFI roundtrip

这是测试层 / 调试层入口，不属于生产主流程。

## 6. 抽取链路

当前真实链路如下：

```text
EPUB
→ reader.read_epub()
→ reader.get_spine_documents()
→ extractor.extract_segments()
    → tag_filters.match_element_policy() / get_extract_action()
    → _collect_text_spans()
    → _trim_spans()
    → cfi.generate_cfi_for_text_range()
    → sentence_splitter.split()            # 句子级时
    → _map_sentences_to_segments()
→ list[Segment]
```

对应回提链路：

```text
Segment.cfi
→ cfi.resolve_cfi()
→ extractor.extract_text_from_cfi()
→ 与当前抽取规则一致的可读文本
```

## 7. 当前启发式边界

当前已经接受的设计现实：

1. 这一步不做语义级正文识别
2. 只对结构层、标签层、局部格式层做尽量稳健的启发式
3. 对“结构健康”的 EPUB，尽量输出可对齐句子
4. 对“结构不健康”的 EPUB，允许残留部分非正文、断句不理想、meta 泄漏

这也是当前项目最重要的边界定义。

## 8. 已解决的问题

目前已完成或明显缓解的点：

1. ruby / rt / rp 的抽取策略化
2. superscript / footnote / noteref 降噪
3. 段落和句子共用同一套 normalize / span 体系
4. CFI roundtrip 与正文定义统一
5. 句子级 CFI 稳定生成
6. 批量 Markdown 报告与 reader-style 审阅链路
7. 一部分 TOC / license / page-marker / heading 类噪音过滤
8. 一部分对白和引号边界后处理

## 9. 暂不处理的问题

以下问题当前明确留到后续阶段：

1. 诗行 / 诗歌排版保真
2. 按 EPUB 类型做更深层适配
3. 语义级正文甄别
4. 语义级句子修正
5. 对极差 EPUB 做“修复型抽取”

这些问题之后更适合通过“书籍类型适配层”或“语义后处理层”来解决。

## 10. 下一步方向

当前设计下，下一步更合理的路线不是继续堆更多局部标签判断，而是：

1. 增加一层“EPUB 类型 / 生成器风格适配”
2. 把 paratext / navigation / backmatter 过滤做成更系统的候选健康度模型
3. 在抽取完成后，把语义判断交给后续对齐或质量筛选模块
4. 保持 extractor 只做“结构启发式尽力而为”，不承担过多语义职责

这也是当前代码和测试体系所对应的长期方向。
