# BookAlign 技术细节

本文档说明 BookAlign 当前的实现方式、已知不足，以及为什么它现在会长成一个“EPUB 对齐 + 重建”工具。

## 1. 整体思路

BookAlign 的核心目标不是翻译，而是把两本已经存在的书：

- 一本原著 EPUB
- 一本正式译本 EPUB

整理成可对照阅读的单本 EPUB。

正式 pipeline 目前是：

```text
source EPUB + target EPUB
-> filtered_preserve extraction
-> structured chapter matching
-> Bertalign sentence / paragraph alignment
-> source-layout EPUB rebuild
```

这里最重要的设计取舍是两点：

1. 尽量只让正文参与对齐，降低目录、脚注、后记把全文拖偏的概率。
2. 非正文信息不在抽取阶段丢掉，而是保留到 builder 阶段再处理。

## 2. 核心数据模型

### `Segment`

定义位置：

- `bookalign/models/types.py`

`Segment` 是整个系统里的最小工作单元。它既是对齐输入，也是回写定位锚点。

关键字段：

- `text`: 当前句段或段落文本
- `cfi`: 当前单元的 EPUB CFI
- `paragraph_cfi`: 所属段落锚点
- `chapter_idx / paragraph_idx / sentence_idx`: 结构位置
- `raw_html`: 原始块级 HTML
- `text_start / text_end`: 句子在段落中的字符范围
- `has_jump_markup / jump_fragments / is_note_like`: 注释与超链接元数据
- `alignment_role`: `align` 或 `retain`
- `paratext_kind`: `body / toc / note_body / chapter_heading / frontmatter / backmatter / metadata / unknown`
- `filter_reason`: 启发式判定原因

### `AlignmentResult`

`AlignmentResult` 是抽取与 builder 之间的稳定中间层。

关键字段：

- `pairs`: 对齐后的 `AlignedPair[]`
- `source_lang / target_lang`
- `granularity`
- `extract_mode`
- `retained_source_segments`
- `retained_target_segments`

它有两个用途：

- 保存正式对齐结果
- 作为 builder-only 调试输入，避免反复重跑模型

## 3. EPUB 抽取

相关模块：

- `bookalign/epub/reader.py`
- `bookalign/epub/tag_filters.py`
- `bookalign/epub/extractor.py`
- `bookalign/epub/cfi.py`
- `bookalign/epub/sentence_splitter.py`

当前抽取策略是 `filtered_preserve`。

这套策略不会把所有可见文本一股脑塞给对齐器，而是先做粗分类：

- 正文：进入 `alignment_segments`
- 目录、注释正文、章节标题、前后附文等：进入 `retained_segments`

抽取阶段还会做几件关键事情：

- 生成段落级和句子级 CFI
- 保留原始 HTML 片段供 builder 尽量复原
- 记录脚注引用、回跳链接和锚点信息
- 为句子保留其在段落中的范围，方便 inline 模式重建

## 4. 章节匹配与对齐

章节匹配在 `bookalign/pipeline.py` 里完成，默认使用 `structured` 模式。

它不是简单按章节标题做字符串匹配，而是结合顺序约束和文本信号做顺序 DP，尽量避免整本书在中段发生章节错位。

正文对齐由 `bookalign/align/bertalign_adapter.py` 封装的 Bertalign 完成。

当前实际使用的是：

- 多语句向量模型
- embedding 相似度
- 动态规划对齐

它支持：

- `1-1`
- `1-N`
- `N-1`
- `N-M`
- `1-0 / 0-1`

这比“每句检索最像的一句”要稳得多，尤其适合文学翻译里常见的拆句、并句、增补和省略。

## 5. 为什么保留 JSON

对齐阶段最贵，builder 调整最频繁。

所以 BookAlign 把 `AlignmentResult` 单独保存成 JSON，是个有意为之的工程选择。这样做有几个直接好处：

- 改样式或 builder 逻辑时，不必重新跑模型
- 可以专门分析错位窗口
- 可以把“对齐问题”和“重建问题”拆开调试
- 方便后续做局部修正、回归测试和人工审阅

## 6. EPUB 重建

相关模块：

- `bookalign/epub/builder.py`
- `bookalign/pipeline.py`

目前有两种主要输出思路：

- `simple`: 重新生成一本文本块式双语 EPUB
- `source_layout`: 基于原著 EPUB 结构回写译文

公开使用时更推荐 `source_layout`，因为阅读体验更自然。

### `paragraph` 模式

把译文按段落写回到原段后面。

优点：

- 更稳
- 对 source EPUB 结构破坏更小
- 对阅读器兼容性更好

缺点：

- 译文颗粒度较粗

### `inline` 模式

在原 block 内做“原句 -> 译句”交错回写。

优点：

- 对照最紧密
- 更适合语言学习和细读

缺点：

- 更依赖句内定位和段内结构
- 更容易被脏 EPUB 样式、嵌套标签和异常换行拖坏

## 7. 注释与未对齐内容

这是 EPUB builder 最麻烦的一块。

当前处理原则是：

- 注释正文不参与正文对齐
- 注释与其他 retained 内容仍然保存在 JSON 里
- builder 会把注释和非注释 retained 内容分别写入附加 XHTML
- 正文中的注释引用会被改写成可点击的脚注标记
- 注释页中的回跳链接会指回重建后的正文锚点

此外，目标书里那些整章未匹配、但本身确实存在的正文或附文，也会进入 `retained_target_segments`，不会在 JSON 里直接丢失。

## 8. 当前不足

### EPUB 格式健康度影响太大

现实里的 EPUB 非常脏。

常见问题包括：

- TOC 空链接
- 注释 DOM 结构极不统一
- 把一整章打碎成大量 span
- 段落和换行混用
- 大量与正文混杂的导读、附录、元数据

这意味着很多工程时间花在“兼容烂格式”上，而不是对齐算法本身。

### 语言覆盖还不够宽

现在最稳定的是：

- 日文原著 -> 中文译本
- 英文原著 -> 中文译本

西语链路已经能跑，但仍比不上前两者稳。

### 文学文本天生不是规整并行语料

文学译本里很常见：

- 拆句
- 合句
- 倒装
- 解释性增译
- 修辞替换

这使得“句子级”天然不是一个绝对稳定的金标准，只能尽量逼近可阅读的结果。

### 现在的工具形态还不是最终形态

把结果固化成 EPUB 是目前最现实的落地方式，但不是最理想的终局。

更理想的形态应该是：

- 直接进入阅读器
- 支持句对展开/收起
- 支持错位窗口人工修正
- 支持阅读过程中的即时回看与注释

## 9. 后续方向

### 更强的局部修正

当前已经有局部窗口重对齐能力，但还可以继续做：

- 更稳的断链检测
- 更保守的窗口回退策略
- builder 前的自动异常扫描

### 更好的阅读器适配

后面值得补的方向包括：

- 缩进与段间距策略
- 注释样式统一
- 深色模式与更多阅读器兼容性测试
- 对图片、图注、诗歌等页面的专门处理

### 从“离线工具”走向“阅读器组件”

这是我认为更合理的长期方向。

当前工具更像一个可用原型，证明“正式译本 + 原著 + 自动对齐 + EPUB 重建”这件事是可落地的；真正的产品形态，应该是阅读器里的对照阅读能力，而不是单独导出一个 EPUB 文件。
