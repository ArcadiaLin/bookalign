# BookAlign 技术路线

本文档说明 BookAlign 当前的实现方式、为什么仓库里同时保留 pipeline 和 skill 两条路径，以及当前推荐的技术路线。

## 1. 当前推荐路线

BookAlign 现在有两条实际可用的运行路线：

1. `bookalign` CLI one-shot pipeline
2. `skills/bookalign-labse` review-first workflow

当前推荐路线是第二条，也就是 skill-first。

原因不是因为 CLI 失效了，而是因为真实 EPUB 的噪声远比“干净平行文本”复杂：

- front matter 会把正文章节整体推偏
- `chapter_id` 和 sentence-level record 归属不一定稳定一致
- 一个 visible chapter 里可能混进注释、评论、目录残留、年谱、附文
- 有些书只能安全地按 slice 逐段对齐，而不能整章或整书一把跑完

所以当前技术路线已经从“单条 whole-book pipeline”转成：

```text
environment check
-> extraction
-> chapter / sentence consistency review
-> mixed-content inspection
-> explicit slice planning
-> local alignment per slice
-> unmatched-region review
-> final EPUB build
```

CLI pipeline 仍然保留，主要面向：

- 输入结构比较干净的书
- 快速试跑
- 生成初版 alignment JSON
- builder-only 回归

## 2. 两条路径的职责边界

### CLI pipeline

CLI 代表仓库里的直接编排路径，核心入口在：

- `bookalign/cli.py`
- `bookalign/pipeline.py`

它当前仍然是 one-shot 逻辑：

```text
source EPUB + target EPUB
-> filtered_preserve extraction
-> heuristic chapter matching
-> Bertalign alignment
-> EPUB build
```

这里的章节匹配仍然存在，但应理解为启发式章节建议，而不是 production 级真值层。

### Skill workflow

推荐 workflow 在：

- `skills/bookalign-labse/SKILL.md`
- `skills/bookalign-labse/references/workflow.md`
- `skills/bookalign-labse/references/production-workflow.md`

这条路径显式强调：

- 先问清解释器、模型路径、远程推理策略、artifacts 目录
- 先做环境检查，再决定 backend
- 先看章节，再信任 `chapter_id`
- 先做一致性自检，再决定是否按 chapter 对齐
- 只有 clean slice 才进入 production build

这也是当前更符合真实书籍数据的工程路线。

## 3. 核心数据模型

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

现在它除了保存已对齐内容，还承担两类重要职责：

- 保存未对齐的单边 pair，供后续 review
- 作为 builder-only 调试输入，避免反复重跑模型

## 4. EPUB 抽取

相关模块：

- `bookalign/epub/reader.py`
- `bookalign/epub/tag_filters.py`
- `bookalign/epub/extractor.py`
- `bookalign/epub/cfi.py`
- `bookalign/epub/sentence_splitter.py`

当前抽取策略是 `filtered_preserve`。

它不会把所有可见文本一股脑塞给对齐器，而是先做粗分类：

- 正文：进入 `alignment_segments`
- 目录、注释正文、章节标题、前后附文等：进入 `retained_segments`

抽取阶段还会做几件关键事情：

- 生成段落级和句子级 CFI
- 保留原始 HTML 片段供 builder 尽量复原
- 记录脚注引用、回跳链接和锚点信息
- 为句子保留其在段落中的范围，方便 inline 模式重建

## 5. 章节匹配已经不是唯一锚点

这是当前路线里最重要的变化之一。

早期可以把章节匹配理解成：

```text
抽章节 -> 章节对齐 -> 句子对齐
```

但现在不能再把 `chapter_id` 当作绝对稳定锚点。

实际问题包括：

- `list_book_chapters(...)` 看到的 chapter 和 sentence record 归属可能漂移
- 一个 `chapter_id` 内可能并进多个正文部分
- 段落索引在同一个 visible chapter bucket 内可能重置
- front matter / chronology / note block 可能混进正文段

因此当前推荐做法是：

1. 先看 `list_book_chapters(...)`
2. 再看 `get_chapter_preview(...)`
3. 再看 `get_chapter_structure(...)`
4. 再抽样 `sentence_segments`
5. 只有这几个视图一致时，才让章节信息进入正式切片计划

换句话说，章节匹配现在更像“候选建议层”，不是最终执行层。

## 6. 对齐层

正文对齐仍然由 Bertalign 路线负责，封装在：

- `bookalign/align/bertalign_adapter.py`
- `bookalign/align/aligner.py`

它的基础能力仍然是：

- 多语句向量模型
- embedding 相似度
- 动态规划对齐

支持：

- `1-1`
- `1-N`
- `N-1`
- `N-M`
- `1-0 / 0-1`

这仍然比“每句检索最像的一句”稳得多，尤其适合文学翻译中的拆句、并句、增补和省略。

当前工程变化主要不在算法核，而在执行边界：

- 不再默认整书隐式配对
- production 路径要求显式 `slice_plan`
- 一轮结束后要求直接复查未对齐段落

## 7. 为什么要保留 JSON 与 review artifact

对齐阶段最贵，人工判断最容易反复发生，builder 调整又最频繁。

所以 BookAlign 把中间产物显式保存下来，是当前路线的一部分，而不是附带功能。

保留这些 artifact 的直接好处：

- 改样式或 builder 逻辑时，不必重新跑模型
- 可以单独分析错位窗口
- 可以把“对齐问题”和“重建问题”拆开调试
- 可以把未对齐区域单独抽出来复看
- 可以在 build 前形成 review checkpoint

当前比较重要的 artifact 包括：

- `source_extraction.json`
- `target_extraction.json`
- `slice_manifest.json`
- `alignment.json`
- `alignment_report.json`
- `review.html`

## 8. Builder 路线

相关模块：

- `bookalign/epub/builder.py`
- `bookalign/pipeline.py`

目前有两种主要输出思路：

- `simple`: 重新生成一本文本块式双语 EPUB
- `source_layout`: 基于原著 EPUB 结构回写译文

公开使用时更推荐 `source_layout`，因为阅读体验更自然，也更符合这个项目的目标。

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

### 当前 builder 的新增默认行为

当前中文译文段落在 build 时默认写入两个空格的段首缩进。

这是一个明确的阅读排版选择，不再只是 CSS 视觉缩进。

## 9. 注释、retained 内容与未对齐段落

这是 builder 最麻烦的一层，也是 skill-first 路线存在的重要原因。

当前处理原则是：

- 注释正文不参与正文对齐
- retained 内容仍然保存在 JSON 里
- builder 会把注释和其他 retained 内容分别写入附加 XHTML
- 正文中的注释引用会被改写成可点击的脚注标记
- 注释页中的回跳链接会指回重建后的正文锚点

另外，一轮对齐后不再只看 summary，而要显式看：

- 哪些 pair 只有 source 没有 target
- 哪些 pair 只有 target 没有 source
- 哪些 unmatched pair 连成了连续区域

这也是 `review_unaligned_segments(...)` 这类接口存在的原因。

## 10. 当前不足

### EPUB 格式健康度影响太大

现实里的 EPUB 非常脏。

常见问题包括：

- TOC 空链接
- 注释 DOM 结构极不统一
- 把一整章打碎成大量 span
- 段落和换行混用
- 大量与正文混杂的导读、附录、元数据

所以当前大量工程时间花在兼容这些输入，而不是单纯优化对齐算法。

### 语言覆盖还不够宽

现在最稳定的是：

- 日文原著 -> 中文译本
- 英文原著 -> 中文译本

西语链路已经能跑，但仍不如前两者稳。

### 文学文本天生不是规整并行语料

文学译本里很常见：

- 拆句
- 合句
- 倒装
- 解释性增译
- 修辞替换

所以“句子级”从来不是绝对稳定的金标准，只能逼近一个可阅读结果。

### CLI whole-book pipeline 仍然过于乐观

即使当前 CLI 还能工作，也不适合承担 production 默认入口。

如果输入书本存在章节漂移、混合正文、评论块或索引重置，whole-book 直跑的风险仍然很高。

## 11. 后续方向

### 继续加强 staged production

接下来更值得继续做的是：

- 更稳的 drift / mixed-content 预检
- 更清晰的 slice planning 表达能力
- builder 前的自动异常扫描
- 更好的 review artifact 组织方式

### 更好的阅读器适配

后面值得补的方向包括：

- 更细的缩进与段间距策略
- 注释样式统一
- 深色模式与更多阅读器兼容性测试
- 对图片、图注、诗歌等页面的专门处理

### 从离线工具走向阅读器组件

这仍然是更合理的长期方向。

当前仓库已经证明“正式译本 + 原著 + 自动对齐 + EPUB 重建”是可落地的；下一阶段更合理的形态，应当是阅读器里的对照阅读能力，而不只是导出一个离线 EPUB。
