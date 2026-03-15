# BookAlign 当前状态

## 总体判断

项目目前处于“抽取与切分底层能力已经成形，但完整双语生成链路尚未完成”的阶段。

现在已经有一条可运行、可测试、可审阅的 EPUB 抽取主线：

1. 读取 EPUB 与 spine 文档
2. 从 XHTML 中抽取段落或句子级 `Segment`
3. 以 `CFI` 为主定位方式保存文本范围
4. 支持 `ja/zh/en/es` 的句子切分
5. 支持 Markdown 报告和 reader-style 抽样审阅

但还没有进入完整的：

1. 语义对齐
2. 双语重建
3. 端到端 CLI / pipeline

## 当前已经稳定下来的部分

### 1. EPUB 读取

文件：

- [reader.py](/home/arcadia/projs/bookalign/bookalign/epub/reader.py)

能力：

1. 读取 EPUB
2. 获取按 spine 顺序排列的 XHTML 文档
3. 提取基础元数据

### 2. CFI 主链路

文件：

- [cfi.py](/home/arcadia/projs/bookalign/bookalign/epub/cfi.py)

能力：

1. 解析 EPUB CFI
2. 解析 range CFI
3. 生成段落和句子的 range CFI
4. 支持 CFI roundtrip 回提

当前结论：

1. 主流程已经明确以 `CFI` 为主
2. `XPath` 不再承担运行时核心定位职责

### 3. 抽取器

文件：

- [extractor.py](/home/arcadia/projs/bookalign/bookalign/epub/extractor.py)

能力：

1. 规则驱动的块级候选抽取
2. 可读文本 span 收集
3. 段落级 `Segment` 生成
4. 句子级 `Segment` 映射
5. `extract_text_from_cfi()` 回提

当前实现特征：

1. 以策略动作驱动节点行为
2. 段级和句级共用同一套 `TextSpan` / normalize 逻辑
3. 支持结构启发式过滤与局部噪音清理

### 4. 策略层

文件：

- [tag_filters.py](/home/arcadia/projs/bookalign/bookalign/epub/tag_filters.py)

能力：

1. `ElementPolicy`
2. `ExtractAction`
3. `match_element_policy()`
4. `get_extract_action()`

当前支持的典型策略：

1. `ruby -> KEEP_CHILDREN_ONLY`
2. `rt/rp -> SKIP_ENTIRE`
3. `br -> INLINE_BREAK`
4. `span.super -> SKIP_ENTIRE`
5. `a.noteref / footnote -> SKIP_ENTIRE`
6. `section/article/header/footer -> STRUCTURAL_CONTAINER`

还包含一层块级候选健康度启发式，用来尽量压掉：

1. license / Gutenberg / obvious metadata
2. heading / navigation-like block
3. 数字页码和分隔符行

### 5. 分句器

文件：

- [sentence_splitter.py](/home/arcadia/projs/bookalign/bookalign/epub/sentence_splitter.py)

当前支持：

1. `ja`
2. `zh`
3. `en`
4. `es`

当前特征：

1. CJK 标点切分
2. `pysbd` 英西文切分
3. 引号/对白后处理
4. `br` 较多时的 line-aware 启发式切分

## 当前测试能力

测试文件：

- [test_splitter.py](/home/arcadia/projs/bookalign/tests/test_splitter.py)
- [test_extractor.py](/home/arcadia/projs/bookalign/tests/test_extractor.py)

调试 / 审阅入口：

- [debug_report.py](/home/arcadia/projs/bookalign/bookalign/epub/debug_report.py)

支持的验证方式：

1. 单元测试
2. 真实 EPUB 集成测试
3. CFI roundtrip 检查
4. Markdown 报告抽样
5. reader-style 多 agent 审阅

最近一次相关测试结果：

```text
19 passed
```

## 当前批量审阅结论

在 `books/` 的 12 本 EPUB 上已经做过多轮 reader-style 抽样审阅。

总体结论：

1. 对结构健康的 prose EPUB，当前抽取链路已经能产出可读、可对齐的句子候选
2. ruby、脚注标记、上标注释、常见 noteref 噪音已经明显改善
3. 当前最主要的问题已经不再是 ruby，而是：
   - paratext / navigation / backmatter 泄漏
   - 对白与引号句界
   - line-break-heavy 结构

这符合当前项目阶段的边界定义：

1. 本层只做“结构启发式尽力而为”
2. 不在这一层追求语义完美的正文识别

## 已知边界

当前明确接受的边界：

1. 不专门处理诗行
2. 不对所有 EPUB 完成语义级正文甄别
3. 对极差 EPUB，仍可能混入 metadata / backmatter / navigation-like 文本
4. 长对白、文学化省略号、复杂引号仍可能切分不理想
5. 图像页 EPUB 无法靠当前文本抽取链路得到正文

## 尚未展开的部分

这些模块还没有进入实质开发：

1. [pipeline.py](/home/arcadia/projs/bookalign/bookalign/pipeline.py)
2. [cli.py](/home/arcadia/projs/bookalign/bookalign/cli.py)
3. [builder.py](/home/arcadia/projs/bookalign/bookalign/epub/builder.py)
4. `align/*` 的完整落地与调优

因此当前项目并不是“对齐器已完成，抽取只是附属”，而是相反：

1. 抽取层是当前主线
2. 对齐和重建将在抽取层稳定之后继续推进

## 下一阶段方向

当前最合理的后续方向是：

1. 增加 EPUB 类型 / 生成器风格适配层
2. 继续收敛 paratext / navigation / backmatter 启发式过滤
3. 在后续模块中增加语义级筛选与修正
4. 推进 `aligner`、`builder`、`pipeline` 的真实落地

简化表述就是：

1. 当前阶段：把“可对齐文本抽取”做稳
2. 下一阶段：把“语义对齐与双语重建”接上
