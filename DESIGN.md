# BookAlign 设计说明

## 1. 设计目标

BookAlign 的目标不是单纯“抽文本”，也不是直接做一个黑盒翻译工具，而是建立一条可追踪、可审阅、可回写的双语 EPUB 工程链路。

当前设计目标分三层：

1. 稳定抽取：从 source/target EPUB 中提取可对齐句子，并尽量保留结构定位。
2. 稳定对齐：在章节和句子两个层面完成可解释的双语对齐。
3. 稳定重建：将对齐结果重新组织为可阅读、可调试的 EPUB。

## 2. 核心设计原则

### 2.1 以 `Segment` 为中心

系统的跨模块公共语言不是 DOM 节点，也不是 XPath，而是 `Segment`。

`Segment` 同时承担：

- 对齐输入文本单元
- 源结构回溯锚点
- builder 注入依据
- 测试与人工审阅的最小工作单元

这让 extractor、aligner、builder 可以解耦迭代，而不需要互相重新解析 EPUB DOM。

### 2.2 以 `CFI` 为主锚点，而不是 XPath

`XPath` 只适合调试，不适合作为生产定位主键。当前系统把 `CFI` 作为主定位方式：

- `Segment.cfi` 表示句子级或段落级范围锚点
- `Segment.paragraph_cfi` 表示该句子所属段落锚点
- `extract_text_from_cfi()` 用于 roundtrip 校验

这使得 source-layout builder 可以在不重跑 extractor 的情况下回到 source XHTML。

### 2.3 抽取层只做启发式，不做语义理解

extractor 的职责是尽量稳定、干净地提取文本，而不是在这一层断言“这一定是正文”。

因此当前策略是：

- 用 `tag_filters` 和段落 heuristics 清理明显噪音
- 对 frontmatter/backmatter 的更强判断放到章节匹配层
- 对最终阅读质量的修正放到 builder 层

当前这层已经明确拆成两条主轴：

- `extract_mode=filtered`：保留现有正文优先的启发式抽取
- `extract_mode=full_text`：除图片/脚本/样式等非文本内容外，目录、注释、前后附文也允许进入 `Segment`
- `extract_mode=filtered_preserve`：抽取范围接近 `full_text`，但启发式命中的非正文只保留、不参与对齐

### 2.4 builder 与 extractor 解耦

本项目明确避免“为了 builder 改坏 extractor 主线”。

因此 builder 当前采取两种策略：

- `simple`: 直接消费 `AlignmentResult`，生成新的双语书
- `source_layout`: 继续消费 `AlignmentResult`，但基于 `paragraph_cfi` 回到 source XHTML 做原结构回写

即使 source-layout 继续升级，也不反向侵入 extractor 的正文定义。

## 3. 模块分层

### 3.1 EPUB 层

位于 `bookalign/epub/`：

- `reader.py`: 读取 EPUB，按 spine 获取文档
- `tag_filters.py`: 元素策略与启发式配置
- `extractor.py`: 生成 paragraph/sentence `Segment`
- `sentence_splitter.py`: 多语言分句
- `cfi.py`: CFI 解析、生成、回提
- `builder.py`: 双语 EPUB 输出
- `debug_report.py`: 人工审阅报告

### 3.2 对齐层

位于 `bookalign/align/`：

- `base.py`: `BaseAligner` 抽象
- `aligner.py`: 通用 pair 构造逻辑
- `bertalign_adapter.py`: vendored `bertalign` 适配器

### 3.3 编排层

位于顶层：

- `pipeline.py`: 抽取、章节匹配、句子对齐、builder 串联
- `cli.py`: 命令行入口

## 4. 关键设计决策

### 4.1 为什么章节匹配不能简单 `zip`

真实书籍里，source 和 target 常常存在：

- 封面不对齐
- 目录结构不对齐
- 版权页数量不同
- 注解、后记、附录只存在于一侧

因此当前 `pipeline.match_extracted_chapters()` 使用顺序 DP：

- 允许 source 侧跳章
- 允许 target 侧跳章
- `structured` 模式下对 paratext 提供更低 skip 成本和更高错配惩罚
- `raw` 模式下尽量不做预筛选，保留对照实验能力

当前推荐绑定关系：

- `filtered` 主轴默认配 `structured`
- `full_text` 主轴默认配 `raw`
- `filtered_preserve` 主轴默认配 `structured`

### 4.2 为什么 source-layout 要拆成 `paragraph` / `inline`

逐句写回 paragraph 内部虽然更理想，但风险明显高于段后插入：

- 容易打碎原始 `ruby`/`span`/`em` 等 inline 结构
- 容易引入阅读器兼容问题
- 对 CFI 定位精度要求更高

因此当前设计是：

- `writeback_mode=paragraph` 继续作为稳定模式保留
- `writeback_mode=inline` 用于句位级回写
- 两者共用同一条 `source_layout` 主链路和同一组元数据修正

这样既保住“结构可控”，也允许持续推进更细粒度回写。

### 4.3 为什么横排不仅要改 CSS，还要改 OPF 方向

部分日文 source EPUB 在 OPF spine 中声明了 `page-progression-direction="rtl"`。

如果只改正文 CSS 为横排，而不改书级阅读方向，某些阅读器仍会：

- 把最后一页当第一页
- 沿用右向左翻页语义
- 上滚/下滚逻辑异常

因此 `source_layout + horizontal` 模式当前会同时：

- 注入横排 CSS
- 将输出书方向设为 `ltr`

这是兼容性修复，而不是纯视觉改动。

## 5. 当前 builder 策略

### 5.1 `simple`

适用于：

- 审查句对质量
- 快速看整体对齐结果
- 不关心原书 XHTML 保真

特点：

- 新建 XHTML 章节页
- 明确展示 source sentence / target sentence
- 结构最简单，最利于对齐诊断

### 5.2 `source_layout`

适用于：

- 保留 source 章节和大体版式结构
- 在原书中读取双语内容
- 检查 CFI 注入是否稳定

特点：

- 保留 source spine 与 source XHTML 文件名
- 保留原始 `<head>` 中的样式链接和标题
- 通过 `writeback_mode` 选择段落级或 inline 级回写
- 默认输出 plain `<p>`，调试元数据可选开启

#### `writeback_mode=paragraph`

- 仍然按段聚合同段译文
- 在命中的 source block 后插入译文 `<p>`
- 风险最低，适合作为稳定基线
- `full_text` 主轴下允许保留 target 注释跳转并重写到输出书中的新锚点
- `filtered_preserve` 主轴下把 target 非正文统一写入新的 synthetic appendix XHTML，而不是塞回正文章节

#### `writeback_mode=inline`

- 保留原始 block 容器本身
- 在同一 block 内按“原句 -> 译句”交错回写
- 段内只插 `<br/>`
- 段与段之间插入 `<p><br/></p>`
- 需要基于 paragraph 内的 live DOM 文本轨迹重建句子片段
- `full_text` 主轴下 target 侧带跳转的句段会尽量保留可点击链接
- `filtered_preserve` 主轴下正文句段保留注释跳转，跳转目标统一改写到 `译文附录`

## 6. 数据流

```text
read_epub()
-> get_spine_documents()
-> extract_segments(..., splitter=SentenceSplitter(...))
-> ExtractedChapter[]
-> match_extracted_chapters()
-> align_segments() / BertalignAdapter.align()
-> AlignmentResult
-> build_bilingual_epub() or build_bilingual_epub_on_source_layout()
-> write_epub()
```

## 7. 当前已验证的工程结论

- extractor 已经可以稳定提供句子级 `Segment`
- `paragraph_cfi` 足够支撑 `source_layout` 的段落锚定
- `text_start` / `text_end` 足够支撑首版 inline 句位回写
- `structured` 章节匹配可在《金阁寺》上避开前后附文错配
- `raw` 模式可作为不做预筛选的对照路径
- `full_text` 主轴已可把目录/译注带入对齐与回写
- `filtered_preserve` 主轴已可复用 filtered 的正文对齐质量，同时保留被过滤出的目录/注释/前后附文
- source-layout 横排输出必须同时修正 CSS 和 OPF 方向

## 8. 当前保留的技术债

- inline 回写对极复杂 inline 结构仍需更多真实书回归
- 还没有更强的对齐质量打分与人工修正接口
- 还没有多本书级别的 builder 样式回归矩阵
- 还没有对极复杂诗歌/图文页建立专门策略

## 9. 下一步推荐方向

1. 继续增强 source-layout 的阅读器兼容性回归。
2. 继续增强 inline 回写对复杂 DOM 的稳定性，而不破坏 extractor 主线。
3. 给 `AlignmentResult` 增加更真实的评分与审阅辅助信息。
4. 建立更系统的 real-book 验证清单，而不是只依赖单本书。
