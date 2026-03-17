# BookAlign 当前状态

## 总体判断

项目现在已经从“抽取主线已成形”推进到“句子级对齐与新 EPUB 生成链路可实际运行”的阶段。

当前已经具备一条真实可跑的端到端链路：

1. 读取原版 EPUB 与译版 EPUB
2. 抽取句子级 `Segment`
3. 基于 `bertalign` 做句子级双语对齐
4. 生成新的双语 EPUB

这条链路已经在 `books/` 中的《金阁寺》日文原版与中文译本上实际跑通，并产出了可读取的双语 EPUB。

但项目还没有进入“结构保真回写原书 XHTML”的阶段。目前的 builder 仍然是生成一部新的双语阅读 EPUB，而不是把译文精确插回源书原始 DOM。

## 当前已经稳定下来的部分

### 1. EPUB 抽取与定位

文件：

- `bookalign/epub/reader.py`
- `bookalign/epub/extractor.py`
- `bookalign/epub/tag_filters.py`
- `bookalign/epub/sentence_splitter.py`
- `bookalign/epub/cfi.py`

能力：

1. 读取 EPUB 并按 spine 顺序获取 XHTML 文档
2. 用规则 + 策略模型抽取段落和句子级 `Segment`
3. 用 `CFI` 作为主定位方式保存文本范围
4. 支持 `ja/zh/en/es` 的句子切分
5. 支持 `extract_text_from_cfi()` 回提验证

当前结论：

1. extractor 已经是稳定边界
2. 句子级对齐模块直接消费 `Segment`，不需要重新扫描 EPUB DOM
3. 当前对齐与重建工作没有反向干扰现有 EPUB 操作核心

### 2. 句子级对齐链路

文件：

- `bookalign/align/base.py`
- `bookalign/align/aligner.py`
- `bookalign/align/bertalign_adapter.py`
- `bookalign/pipeline.py`

能力：

1. 统一的 `BaseAligner` 抽象
2. `BertalignAdapter` 对 vendored `bertalign` 的项目封装
3. chapter-by-chapter 的句子级对齐编排
4. 对 frontmatter / backmatter 可跳过的章节匹配

本轮新增的关键能力：

1. 不再按 `zip(source_chapters, target_chapters)` 粗暴匹配章节
2. 增加了结构驱动的章节匹配层，优先对齐正文，允许跳过封面、目录、版权、注解、年谱、后记等 paratext
3. 默认 CLI / pipeline 语言方向已经改为更贴近当前主测试集的 `ja -> zh`

### 3. 双语 EPUB 生成

文件：

- `bookalign/epub/builder.py`
- `bookalign/cli.py`

能力：

1. 根据 `AlignmentResult` 生成新的双语 EPUB
2. 按章节与段落顺序输出双语句对
3. 保留 source-only / target-only 的缺失占位
4. 为缺失标题或仅有生成器文件名的章节提供稳定的 fallback 标题

当前产物形态：

1. 每个章节输出为新的 XHTML 页面
2. 每个段落内按句对显示原文与译文
3. 不修改输入 EPUB 本身

## 当前验证结果

### 1. 自动化测试

最近一次全量测试结果：

```text
31 passed in 67.88s
```

这次覆盖包括：

1. 抽取与分句
2. 对齐适配层
3. builder 输出
4. pipeline 编排
5. 《金阁寺》真实 EPUB 集成测试

另外，`pytest.ini` 已限制默认收集到 `tests/`，避免把 `scripts/` 中的运行时脚本误当测试收集。

### 2. Bertalign 运行时验证

当前环境已经验证：

1. `faiss-cpu`
2. `torch`
3. `sentence-transformers`
4. `googletrans`
5. `sentence-splitter`

本地模型验证：

1. 已确认 `/root/model/LaBSE` 可被 `SentenceTransformer` 正常加载
2. 已确认模型在当前环境可运行于 `cuda:0`

### 3. 《金阁寺》真实运行结果

输入：

1. `books/金閣寺 (三島由紀夫) (Z-Library).epub`
2. `books/金阁寺 (三岛由纪夫) (Z-Library).epub`

运行结果：

1. 成功匹配 10 个正文章节
2. 成功生成 3901 个对齐 pair
3. 成功输出一版真实双语 EPUB

输出文件：

1. `tests/artifacts/kinkaku_ja_zh_bertalign.epub`

当前结论：

1. 章节匹配层已经足以处理这组真实书籍中前后附文不对称的问题
2. 句子级对齐与新 EPUB 生成链路已经不再停留在 stub 或 demo 阶段

## 当前边界

项目目前仍然明确保留以下边界：

1. builder 生成的是新的双语 EPUB，不是结构保真地回写原书 XHTML
2. `AlignmentResult.score` 目前仍然是 adapter 默认值，不是真实置信度
3. 章节匹配仍然主要依赖结构、标题与句数启发式，而不是更强的跨章语义匹配
4. paratext / backmatter 过滤在更多 EPUB 风格上仍需继续收敛
5. 复杂对白、诗行、强排版依赖内容仍不是当前优化重点

## 下一阶段方向

下一阶段最合理的工作顺序是：

1. 继续收敛章节匹配与 paratext 过滤，扩大真实书籍覆盖面
2. 为对齐结果增加更可用的质量检查与人工审阅产物
3. 研究“基于 source CFI/segment 的结构保真回写”方案，而不是只生成简化的新书
4. 视需要补充段级对齐模式、对齐置信度和后处理修正层

一句话总结：

BookAlign 现在已经不是只有抽取能力的半成品，而是已经具备“extractor -> bertalign -> bilingual EPUB”可运行主链路的工程版本；下一步重点是把这条链路从“可跑”继续推进到“更稳、更准、更保真”。
