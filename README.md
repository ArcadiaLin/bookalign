# BookAlign

BookAlign 的最终目标，是把一部作品的原版 EPUB 和人工译版 EPUB 做结构化抽取、句段对齐，并重建成可直接阅读的双语 EPUB。

当前项目还没有完成整条双语生成链路，但抽取层已经是主线，并且后续工作也将继续围绕这个最终目标推进：先稳定抽取与定位，再接入对齐与重建。

## 最终目标

项目最终希望提供一条完整链路：

```text
原版 EPUB + 译版 EPUB
→ 结构化抽取
→ 句段级对齐
→ 双语内容重建
→ 可在阅读器中直接打开的双语 EPUB
```

最终产物的理想形态是：

1. 支持段落级或句子级双语对照
2. 保留原书章节结构和尽可能多的可用样式信息
3. 保持原文与译文的可回溯定位能力
4. 能适应不同 EPUB 来源和不同 XHTML 风格

## 当前阶段目标

当前阶段不追求“语义完美挑出正文”，而是优先把底层能力做稳：

1. 从结构相对健康的 EPUB 中抽出可对齐的段落和句子
2. 对常见噪音做规则层面的过滤和降噪
3. 用 `CFI` 保存稳定的文本范围锚点
4. 保证段落级和句子级抽取逻辑一致
5. 为后续语义对齐模块提供尽可能干净的输入

这一步的边界是明确的：

1. 这里只做启发式抽取，不做完整语义理解
2. 后续更高层的正文甄别、对齐修正、生成控制，交给后续模块

## 当前已经实现的能力

### EPUB 读取

- 读取 EPUB
- 获取按 spine 顺序排列的 XHTML 文档
- 提取基础元数据

代码：

- [reader.py](/home/arcadia/projs/bookalign/bookalign/epub/reader.py)

### 规则驱动抽取

当前抽取层已经升级为“规则 + 策略”模型，而不只是简单的 skip filter。

支持：

1. `ElementPolicy`
2. `ExtractAction`
3. 标签级与属性级联合匹配
4. 节点行为分发，而不是散落在 extractor 里的标签特判

典型行为：

1. `ruby` 保留 base text
2. `rt/rp` 跳过
3. `span.super`、`a.noteref`、footnote / toc 容器跳过
4. `br` 作为轻量分隔信号
5. 结构容器不直接当正文段落

代码：

- [tag_filters.py](/home/arcadia/projs/bookalign/bookalign/epub/tag_filters.py)

### 段落与句子级 Segment 生成

当前主模型是 `Segment`。

它保存：

1. `text`
2. `cfi`
3. `chapter_idx`
4. `paragraph_idx`
5. `sentence_idx`
6. `raw_html`

并通过 `TextSpan` 保留句级切片和 CFI 映射所需的 trace 信息。

代码：

- [extractor.py](/home/arcadia/projs/bookalign/bookalign/epub/extractor.py)
- [types.py](/home/arcadia/projs/bookalign/bookalign/models/types.py)

### CFI 主定位

当前运行时主定位方式是 `CFI`，不是 `XPath`。

已经支持：

1. 生成段落级 range CFI
2. 生成句子级 range CFI
3. 用 `extract_text_from_cfi()` 做 roundtrip 回提

代码：

- [cfi.py](/home/arcadia/projs/bookalign/bookalign/epub/cfi.py)

### 多语言分句

当前支持：

1. `ja`
2. `zh`
3. `en`
4. `es`

并做了：

1. CJK 标点切分
2. 英西文 `pysbd` 切分
3. 对白 / 引号边界后处理
4. `br` 较多段落的 line-aware 启发式切分

代码：

- [sentence_splitter.py](/home/arcadia/projs/bookalign/bookalign/epub/sentence_splitter.py)

### 测试与人工审阅

项目已经具备两类验证能力：

1. 程序化测试
2. Markdown 报告 + reader-style 审阅

调试报告入口：

- [debug_report.py](/home/arcadia/projs/bookalign/bookalign/epub/debug_report.py)

相关测试：

- [test_splitter.py](/home/arcadia/projs/bookalign/tests/test_splitter.py)
- [test_extractor.py](/home/arcadia/projs/bookalign/tests/test_extractor.py)

## 当前项目边界

当前明确暂不解决的问题：

1. 诗行 / 诗歌排版保真
2. 对所有 EPUB 的语义级正文识别
3. 对极差 EPUB 的完全修复型抽取
4. 图像页 EPUB 的 OCR 或图文恢复

这意味着 BookAlign 当前的抽取层目标不是“任何 EPUB 都完美恢复正文”，而是：

1. 对结构健康的 EPUB，尽量抽出可对齐句子
2. 对结构不健康的 EPUB，尽量减少噪音污染
3. 把剩余问题留给更高层的语义任务或后续适配层

## 接下来将继续朝什么方向推进

之后的工作，将继续围绕最终目标推进，但顺序会保持清晰：

### 第一优先级

继续增强抽取层的可用性和可适配性：

1. EPUB 类型 / 生成器风格适配
2. paratext / navigation / backmatter 的候选过滤
3. 句界规则的继续收敛

### 第二优先级

把抽取结果接入真正的对齐链路：

1. `align/*` 模块落地
2. 对齐结果数据结构稳定化
3. 段级 / 句级双模式对齐

### 第三优先级

落地重建与交付链路：

1. `builder`
2. `pipeline`
3. `cli`
4. 双语 EPUB 输出

## 当前目录

主代码：

```text
bookalign/
├── epub/
├── models/
├── align/
├── cli.py
└── pipeline.py
```

测试与审阅：

```text
tests/
├── test_extractor.py
├── test_splitter.py
├── test_aligner.py
├── test_builder.py
└── artifacts/
```

文档：

```text
README.md
DESIGN.md
STATUS.md
EPUB_EXTRACTION.md
EXTRACTION_REFACTOR.md
```

## 开发说明

运行当前抽取相关测试：

```bash
python -m pytest tests/test_splitter.py tests/test_extractor.py -q
```

生成 Markdown 抽样报告：

```bash
python -m bookalign.epub.debug_report \
  --book kinkaku.epub \
  --seed 20260315 \
  --sample-count 5 \
  --test-type complex \
  --granularity sentence \
  --language ja \
  --debug \
  --output tests/artifacts/sample_report.md
```

## 一句话总结

BookAlign 当前不是“已经完成的双语 EPUB 工具”，而是一个正在向“可稳定抽取、可定位、可对齐、可重建的双语 EPUB 系统”推进的工程。后续工作将继续以这个目标为准，而不是只做零散脚本修补。
