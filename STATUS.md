# BookAlign 项目目标、方案与当前进度

## 1. 项目核心目标

BookAlign 的目标是对两本不同语言的 EPUB 电子书进行结构化处理、文本抽取、句段切分与对齐，最终生成适合阅读器使用的双语 EPUB。

当前项目的核心问题可以概括为三层：

1. 如何从不同来源、不同语言、不同 XHTML 结构的 EPUB 中稳定抽取“可读文本”。
2. 如何在尽量保留原书结构定位能力的前提下，对段落和句子进行切分。
3. 如何将原文与译文做段级或句级对齐，并用于双语重建。

其中，当前阶段最关键的底层能力不是对齐本身，而是：

1. EPUB 章节读取
2. XHTML 正文段落抽取
3. 基于 CFI 的结构定位
4. 面向多语言的句子切分

如果抽取与切分不稳定，后续对齐质量就无法保证。


## 2. 原始设计思路

`DESIGN.md` 给出的整体思路是：

1. 以 `reader` 读取 EPUB 和 spine 文档。
2. 以 `extractor` 从 XHTML 中抽取段落或句子级 `Segment`。
3. `Segment` 除了保存可读文本外，还应尽量保留原始结构定位信息。
4. 通过 `sentence_splitter` 做多语言句子切分。
5. 后续再接入 `aligner`、`builder`，完成双语 EPUB 的重建。

设计文档中曾设想 `Segment` 既保存可读文本，也保存原始结构映射，例如：

1. 原始 XHTML 的位置
2. 可回溯的 span 信息
3. 可用于章节内精确定位的 CFI

这一方向的关键点是：

1. 面向阅读器和 EPUB 生态，`CFI` 是更自然的定位手段。
2. 可读文本不应直接等于原始 XHTML 文本，而应经过规则清洗。
3. 注音、脚注标号、导航结构、目录包装器等应被过滤或降噪。


## 3. 当前仓库的实际实现情况

截至目前，仓库中的模块状态大致如下。

### 3.1 已有基础模块

已存在并可运行的核心模块：

1. [reader.py](E:\workspace\projs\bookalign\bookalign\epub\reader.py)
   - 负责读取 EPUB
   - 获取 spine 顺序文档
   - 提取基础元数据

2. [cfi.py](E:\workspace\projs\bookalign\bookalign\epub\cfi.py)
   - 提供 EPUB CFI 的解析与解析结果定位
   - 支持 range CFI 的生成与解析
   - 提供基础的 CFI 文本提取能力

3. [extractor.py](E:\workspace\projs\bookalign\bookalign\epub\extractor.py)
   - 负责从 XHTML 中抽取段落/句子 segment
   - 现在已经围绕 CFI 主路径完成了一轮增强

4. [sentence_splitter.py](E:\workspace\projs\bookalign\bookalign\epub\sentence_splitter.py)
   - 提供多语言句子切分接口
   - 当前已支持 `ja/zh/en/es` 基础切分策略

5. [tag_filters.py](E:\workspace\projs\bookalign\bookalign\epub\tag_filters.py)
   - 定义 XHTML 标签过滤规则
   - 当前已支持 tag/class/epub:type/role/id/href 级别的过滤

6. [types.py](E:\workspace\projs\bookalign\bookalign\models\types.py)
   - 定义 `Segment`、`AlignmentResult` 等数据结构

### 3.2 尚未真正展开的模块

以下模块在设计中存在，但当前仓库仍基本为空壳或未进入实质开发阶段：

1. `pipeline`
2. `cli`
3. `align/*`
4. `builder`

因此，项目目前仍处于“抽取与切分底层能力建设阶段”，还没有进入完整双语生成链路。


## 4. 当前数据模型的实际方向

在这一轮调整后，`Segment` 的定位能力重新收敛到“以 CFI 为主，以 trace 为辅”的方向。

当前 [types.py](E:\workspace\projs\bookalign\bookalign\models\types.py) 中的关键结构包括：

1. `Segment`
   - `text`：清洗后的可读文本
   - `cfi`：段落或句子的 range CFI
   - `chapter_idx / paragraph_idx / sentence_idx`
   - `raw_html`
   - `element_xpath`
   - `spans`

2. `TextSpan`
   - 用于记录一段可读文本在 XHTML 中的来源
   - 包括源 XPath、文本节点索引、字符偏移
   - 同时记录该 span 如何映射回 paragraph-relative CFI 边界

这里需要强调：

1. `XPath` 现在主要用于调试和测试样本发现。
2. `CFI` 仍然是 segment 的主定位信息。
3. `spans` 的作用是帮助句级切分后仍保留结构可追踪性。


## 5. 当前抽取方案

### 5.1 总体原则

当前抽取方案遵循以下原则：

1. 先通过规则从 XHTML 中找到正文块级元素。
2. 再从块级元素内部提取“可读文本”。
3. 对可读文本生成对应的 `Segment`。
4. 通过 range CFI 对该 `Segment` 做定位。
5. 如果需要句级切分，则基于段落文本继续切句，并为每个句子生成句级 segment。

### 5.2 标签过滤策略

当前 [tag_filters.py](E:\workspace\projs\bookalign\bookalign\epub\tag_filters.py) 已支持以下过滤能力：

1. 跳过 `rt`、`rp`、`script`、`style`、`svg`、`img` 等无正文意义标签。
2. 跳过 `super`、`noteref`、`footnote-ref`、`annotation`、`toc` 等 class。
3. 跳过带有特定 `epub:type`、`role`、`id pattern`、`href fragment pattern` 的脚注/导航节点。
4. 识别明显的结构包装块，避免把目录容器、section 包装器当成正文段落。

### 5.3 可读文本提取

当前 [extractor.py](E:\workspace\projs\bookalign\bookalign\epub\extractor.py) 中的逻辑是：

1. 保留正文需要的内联文本。
2. 对注音、脚注引用、导航类节点做跳过。
3. 对空白字符做标准化。
4. 将 XHTML 中的可读文本片段收集成 `TextSpan` 列表。

这样得到的结果既有：

1. 面向阅读对齐的干净文本
2. 又保留了返回原文结构的 trace 信息

### 5.4 CFI 主路径

这一轮实现的重点，是把抽取流程重新拉回到 CFI 主路径上。

当前 extractor 的处理方向是：

1. 段落级 segment 生成时直接生成 paragraph range CFI。
2. 句级 segment 生成时根据 span 子集映射出句级 CFI。
3. 新增 `extract_text_from_cfi()`，可以从已有 segment 的 CFI 反解回正文节点，再按当前规则提取可读文本。

这意味着当前代码已经具备以下闭环能力：

1. XHTML -> Segment(text + cfi)
2. Segment.cfi -> XHTML 节点范围
3. 节点范围 -> 再次规则清洗 -> 可读文本

这正是当前项目最需要稳定下来的能力。


## 6. 当前分句方案

当前 [sentence_splitter.py](E:\workspace\projs\bookalign\bookalign\epub\sentence_splitter.py) 已做了第一轮多语言适配。

### 6.1 支持语言

当前主要覆盖：

1. 日文 `ja`
2. 中文 `zh`
3. 英文 `en`
4. 西班牙文 `es`

### 6.2 具体策略

1. `ja/zh`
   - 以 CJK 句末标点切分为主
   - 尽量把结尾引号、括号并入句尾
   - 对切分前后的文本做归一化

2. `en/es`
   - 使用 `pysbd` 作为基础切分器
   - 再对 EPUB 抽取中常见的空白和字符噪声做归一化

### 6.3 当前限制

当前分句器仍有若干已知边界：

1. 面对极端复杂的引号嵌套时，仍可能依赖后续规则补充。
2. 部分电子书文本本身带有 OCR 或编码噪声，会直接影响切分质量。
3. 某些“单句但无明显句末标点”的段落，目前以“退化为单句 segment”的方式保留，不强制拆分。


## 7. 本轮完成的工作

这一轮完成的部分，主要集中在“多语言 EPUB 分句抽取测试”和“围绕 CFI 的抽取增强”。

### 7.1 完成了真实 EPUB 集成测试

已补充 [test_extractor.py](E:\workspace\projs\bookalign\tests\test_extractor.py)：

1. 直接从 `books/` 中选取真实 EPUB。
2. 当前覆盖了四种语言：
   - `ja`
   - `en`
   - `es`
   - `zh`
3. 采用固定随机种子抽样，保证每次运行结果可复现。
4. 对每本书随机抽取章节和复杂标签段落。
5. 用当前 extractor 和 splitter 进行段级、句级抽取。
6. 验证 segment 是否包含有效 CFI。
7. 验证抽取结果是否为干净文本。
8. 验证句子重组后是否与段落文本一致。
9. 验证 segment 的 CFI 能否再次回读出有效文本。

### 7.2 测试中 XPath 的角色被收敛

根据当前实现调整，测试里：

1. XPath 只用于“发现复杂结构段落样本”。
2. 不再把 XPath 当作 segment 的主定位依据。
3. segment 的有效性验证以 CFI 为主。

这与项目目标更加一致，也更贴近 EPUB 实际使用方式。

### 7.3 完成了 CFI round-trip 能力补强

在 [extractor.py](E:\workspace\projs\bookalign\bookalign\epub\extractor.py) 中新增了：

1. `extract_text_from_cfi()`

它用于：

1. 通过 `Segment.cfi` 反解到原章节节点
2. 再按当前过滤规则提取可读文本
3. 验证 CFI 是否真实可用

这是当前实现中非常关键的一步，因为它保证了：

1. segment 不是“只保存了一个字符串”
2. 而是确实能够回到原书结构

### 7.4 完成了 span trace 补强

当前 `Segment.spans` 已经重新补回，并用于：

1. 跟踪可读文本来源
2. 把句级 segment 映射回段落中的位置
3. 辅助句级 CFI 生成

### 7.5 完成了过滤规则扩展

这轮已经把过滤规则从简单集合扩展为更可扩展的规则表，已覆盖：

1. 注音标签
2. 脚注引用
3. 导航节点
4. 目录容器
5. 明显非正文包装结构


## 8. 当前测试结果

当前测试已通过：

1. [test_splitter.py](E:\workspace\projs\bookalign\tests\test_splitter.py)
2. [test_extractor.py](E:\workspace\projs\bookalign\tests\test_extractor.py)

执行命令：

```bash
uv run pytest tests/test_splitter.py tests/test_extractor.py
```

结果：

```text
7 passed in 55.91s
```

同时，测试会输出一份审计结果文件：

1. [epub_extraction_audit.jsonl](E:\workspace\projs\bookalign\tests\artifacts\epub_extraction_audit.jsonl)

该文件用于查看本轮抽样到的段落、对应文本和句子切分结果。


## 9. 当前项目进度判断

如果从整体路线看，当前项目大致处于以下阶段：

### 已基本完成

1. EPUB 读取基础能力
2. CFI 解析与基本生成
3. XHTML 正文段落抽取初版
4. 多语言句子切分初版
5. 基于真实 EPUB 的抽取/切分回归测试
6. 以 CFI 为主路径的 segment 回读验证

### 已完成但仍需继续打磨

1. 多语言复杂 XHTML 结构下的抽取稳定性
2. 句级 CFI 边界映射
3. 标签过滤规则的可扩展性
4. 日文/中文/西文混合结构中的边缘案例处理

### 尚未真正展开

1. 双语对齐主流程
2. vecalign / bertalign 集成
3. 双语 EPUB builder
4. CLI / pipeline 的完整打通


## 10. 下一步建议

结合当前代码与进度，下一步建议按以下顺序推进。

### 第一优先级：继续巩固抽取层

建议继续补充以下测试：

1. 更强的 ruby/脚注/目录混合样本
2. 同一段落多层内联标签嵌套样本
3. 句级 CFI 回读后与句子文本一致性的更严格校验
4. 针对中文 EPUB 的更复杂正文样本

### 第二优先级：明确 CFI 与 trace 的职责边界

建议在实现层明确：

1. `CFI` 是主定位信息
2. `spans` 是用于切句和调试的辅助映射
3. `raw_html` 用于重建时保留结构样式

这样后续 `builder` 和 `aligner` 接入时不会再反复摇摆数据模型。

### 第三优先级：进入对齐与重建

在抽取层稳定后，再推进：

1. 按章节或整书生成 `Segment` 列表
2. 接入对齐器
3. 输出 `AlignmentResult`
4. 进入双语 EPUB builder


## 11. 总结

当前项目仍处于底层能力建设期，但关键方向已经更清晰了：

1. 不是单纯“把 XHTML 文本抓出来”
2. 而是要“生成可读文本，同时保留可回到原书结构的定位信息”
3. 在这个定位信息里，`CFI` 应该是主路径

这一轮完成的工作，主要价值就在于把实现重新收拢到了这一方向上：

1. 测试不再依赖 XPath 做 segment 主定位
2. 抽取结果可以通过 CFI 回到原书
3. 多语言真实 EPUB 的抽样测试已经建立
4. 当前抽取器与分句器已经有了第一套可回归验证的质量基线

这使得项目后续继续做规则扩展、句级边界优化、对齐器接入时，有了相对可靠的基础。
