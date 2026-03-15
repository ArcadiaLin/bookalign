# 当前 EPUB 对齐文本抽取实现说明

本文档描述仓库当前版本中，如何从 EPUB 中抽取“可用于对齐”的文本，以及这一流程里使用的定位方法、关键函数、逻辑链路、测试方式和当前边界。

结论先行：

- 当前实现以 `EPUB CFI` 作为 `Segment` 的主定位方式。
- `XPath` 存在，但主要用于调试、测试审计和追踪文本来源，不是主定位协议。
- 段落和句子都先从 XHTML 块级元素中抽取“可读文本”，再生成对应的 `range CFI`。
- 句子级定位不是直接从 DOM 再找一次句子，而是先在段落级 `TextSpan` 上切片，再映射成句级 CFI。

## 1. 相关模块总览

当前实现主要集中在以下模块：

- `bookalign/epub/reader.py`
- `bookalign/epub/tag_filters.py`
- `bookalign/epub/extractor.py`
- `bookalign/epub/cfi.py`
- `bookalign/epub/sentence_splitter.py`
- `bookalign/models/types.py`
- `tests/test_extractor.py`
- `tests/test_splitter.py`

它们之间的实际关系如下：

1. `reader.read_epub()` 读取 EPUB。
2. `reader.get_spine_documents()` 按 spine 顺序拿到 XHTML 文档。
3. `extractor.extract_segments()` 遍历文档中的块级元素。
4. `tag_filters` 负责过滤脚注、目录、注音等不应进入对齐文本的节点。
5. `extractor` 把一个块级元素里的可读文本收集为 `TextSpan` 列表。
6. `cfi.generate_cfi_for_text_range()` 为段落或句子生成 `range CFI`。
7. 句子级场景下，`sentence_splitter` 先切句，再由 `extractor` 把句子映射回对应 span 子区间。
8. `extractor.extract_text_from_cfi()` 和 `cfi.resolve_cfi()` 提供从 CFI 回到文本的验证链路。

## 2. 当前数据结构

当前抽取结果使用 `bookalign/models/types.py` 中两个核心结构。

### 2.1 `Segment`

`Segment` 是参与后续对齐的基本文本单元，字段如下：

- `text`
  清洗后的可读文本。
- `cfi`
  当前主定位字段，保存段落级或句子级 `range CFI`。
- `chapter_idx`
  章节在 spine 中的索引。
- `paragraph_idx`
  章节内段落编号。
- `sentence_idx`
  段落内句子编号；段落级抽取时为 `None`。
- `raw_html`
  原始块级元素 HTML，用于审计和后续重建。
- `element_xpath`
  当前块级元素 XPath，主要用于调试和测试。
- `spans`
  从块级元素中抽出的 `TextSpan` 列表，是句级切片和定位映射的基础。

### 2.2 `TextSpan`

`TextSpan` 表示一小段“可读文本”及其来源位置：

- `text`
- `xpath`
- `text_node_index`
- `char_offset`
- `source_kind`
  当前是 `text` 或 `tail`。
- `cfi_text_node_index`
  该 span 在段落级 CFI 坐标系中的锚点文本节点索引。
- `cfi_exact`
  是否能精确落在父元素的直接文本节点上。

可以把 `TextSpan` 理解为桥梁层：

- 对上连接清洗后的纯文本。
- 对下连接 XHTML 原始结构和 CFI 坐标。

## 3. 当前到底使用 CFI 还是 XPath

当前实现是明确的 `CFI 主路径`。

### 3.1 CFI 的角色

`Segment.cfi` 是段落和句子的主定位信息。生成和解析都围绕它展开：

- 生成入口：`bookalign/epub/cfi.py` 中的 `generate_cfi_for_text_range()`
- 解析入口：`bookalign/epub/cfi.py` 中的 `resolve_cfi()`
- 文本回提入口：`bookalign/epub/extractor.py` 中的 `extract_text_from_cfi()`

这里生成的是 `range CFI`，不是单点 CFI。因为一个可用于对齐的文本单元本质上是一个范围，而不是单一位置。

### 3.2 XPath 的角色

XPath 仍然保留，但用途是辅助性的：

- `Segment.element_xpath` 保存块级元素 XPath，便于测试时定位样本。
- `TextSpan.xpath` 保存 span 来源节点 XPath，便于审计和调试。

当前代码没有把 XPath 当成跨流程的主定位协议，也没有用 XPath 作为对齐结果的最终地址。

### 3.3 为什么不是 XPath 主路径

从当前代码方向看，项目更偏向 EPUB 生态内可移植的定位方式：

- CFI 是 EPUB 规范里的定位机制。
- CFI 可以表达文本范围和字符偏移。
- 对阅读器、重建和后续内容回填更自然。
- XPath 更适合内部调试，不太适合作为最终阅读定位协议。

## 4. 文本抽取的主流程

主入口是 `bookalign/epub/extractor.py` 中的 `extract_segments()`。

逻辑顺序如下。

### 4.1 读取并解析文档

`extract_segments()` 接收：

- `book`
- `doc`
- `chapter_idx`
- `config`
- `splitter`

函数首先通过 `parse_item_xml(doc)` 把 XHTML 解析成 lxml DOM，然后遍历 `root.iter()` 中的节点。

### 4.2 只从块级元素生成 segment

不是所有节点都会变成 `Segment`。当前代码只考虑 `is_block_element(elem, config)` 为真的元素。

块级标签默认来自 `TagFilterConfig.block_tags`，包括：

- `p`
- `div`
- `h1` 到 `h6`
- `blockquote`
- `li`
- `dt`
- `dd`
- `section`
- `article`
- `header`
- `footer`
- `figcaption`
- `pre`

### 4.3 跳过不该成为正文段落的节点

通过两层过滤避免抽出脏文本或结构包装器：

1. `should_skip_element(elem, config)`
2. `is_structural_container(elem, config)`

#### 4.3.1 `should_skip_element()`

定义在 `bookalign/epub/tag_filters.py`，会跳过：

- 明确无正文意义的标签：`rt`、`rp`、`script`、`style`、`svg`、`math`、`img`
- 指向脚注/注释/目录的 class：如 `super`、`noteref`、`footnote-ref`、`annotation`、`toc`
- 规则命中的元素：
  - `a[epub:type=noteref]`
  - `aside[epub:type=footnote]`
  - `nav[epub:type=toc]`
  - `role=doc-toc`
  - `id` 命中 `toc|nav|footnote`
  - `href` 片段命中 `#fn|#footnote|#note`

#### 4.3.2 `is_structural_container()`

它不是在过滤具体噪声文本，而是在避免把纯包装容器误当成段落：

- `section/article/header/footer/nav` 如果内部已有块级子元素，则不生成 segment。
- `div` 如果有两个及以上未跳过的块级子元素，并且自己没有直接文本，也不生成 segment。

这一步的作用是防止同一段正文被多次抽出，或者把章节容器、目录容器抽成文本段落。

### 4.4 从块级元素中收集可读文本 span

真正的正文抽取由 `_collect_text_spans()` 完成，它内部调用 `_iter_readable_text_parts()`。

这是当前实现最关键的部分之一。

#### 4.4.1 DOM 遍历策略

`_iter_readable_text_parts()` 递归遍历一个块级元素内部的内容，并按 DOM 顺序产出 `TextSpan`。

它会处理三类文本来源：

- `node.text`
- `child.tail`
- 内联子元素内部的文本

但它不会无条件深入所有子元素，而是有规则：

- 子元素若命中 `should_skip_element()`，其内部文本跳过，但它的 `tail` 仍可能保留。
- 子元素若本身是块级元素，则不递归进入；块级边界由外层 `extract_segments()` 处理。
- 对内联元素则递归进入，保留其中可读文本。

#### 4.4.2 为什么 ruby 可以保留正文

对于 `<ruby>`，当前并不是整体跳过，而是依赖标签过滤规则跳过 `rt/rp`，保留 ruby 主文本。

例如：

```html
<ruby>舞鶴<rt>まいづる</rt></ruby>から
```

最终抽出的可读文本是：

```text
舞鶴から
```

#### 4.4.3 空白标准化

span 在写入列表前会经过 `_append_span()` 和 `_normalize_fragment()`：

- 把 `NBSP`、全角空格替换为空格
- 删除零宽字符、BOM、软连字符
- 把换行、制表符转为空格
- 折叠连续空白为单个空格
- 避免相邻 span 边界处出现双空格

这意味着当前用于对齐的文本是“清洗后的可读文本”，不是原始 XHTML 文本。

### 4.5 修剪段落首尾空白并确定 CFI 边界

span 收集完后，`extract_segments()` 会调用 `_trim_spans()`。

它做两件事：

1. 去掉段落首尾纯空白 span。
2. 在保留 trace 的前提下，修正首尾 span 的字符偏移，并计算段落的 CFI 起止坐标。

这里涉及三个关键辅助函数：

- `_parent_text_lengths()`
- `_span_start_for_cfi()`
- `_span_end_for_cfi()`

它们负责把 span 映射到“段落相对的文本节点索引 + 偏移”坐标系中。

这一步很关键，因为：

- 有些文本来自父元素直接文本节点，可以精确定位。
- 有些文本来自内联子元素内部，无法直接用父元素文本节点中的字符偏移表达。

当前实现对这两类情况采用不同策略。

#### 4.5.1 `cfi_exact=True` 的 span

如果 span 来自父元素的直接文本节点或可精确映射的位置，CFI 可以定位到：

- 某个 `text_node_index`
- 该文本节点内的 `char_offset`

#### 4.5.2 `cfi_exact=False` 的 span

如果 span 来自内联子节点内部文本，当前实现不会给它构造一个精确的子节点内字符偏移，而是把边界“吸附”到相邻的父级文本节点边界：

- 开始位置吸附到锚点文本节点末尾
- 结束位置吸附到下一个父级文本节点起点

这正是当前句级/段级 CFI 能成立的核心折中：保留可读文本范围，同时在父元素的直接文本节点坐标系里表达这个范围。

### 4.6 生成段落级 `Segment`

如果调用 `extract_segments()` 时没有传入 `splitter`，就直接生成段落级 segment。

生成时会调用：

- `generate_cfi_for_text_range(book, doc, elem, start_tni, start_off, end_tni, end_off, _root=root)`

然后构造：

- `text`
- `cfi`
- `chapter_idx`
- `paragraph_idx`
- `raw_html`
- `element_xpath`
- `spans`

其中 `paragraph_idx` 是以当前文档内实际抽出的段落顺序递增的，不是 DOM 原始块级节点总数。

## 5. 句子级抽取如何工作

句子级不是重新遍历 DOM 去找每个句子，而是在段落级 span 结果基础上继续做映射。

### 5.1 切句入口

如果 `extract_segments()` 收到 `splitter`，它会先对段落文本调用：

- `splitter.split(''.join(span.text for span in trimmed_spans))`

也就是先得到段落级干净文本，再做分句。

### 5.2 分句器行为

`bookalign/epub/sentence_splitter.py` 中的 `SentenceSplitter` 当前逻辑是：

- `ja/zh`
  使用 `_split_cjk()`，按 `。！？!?` 切，并把结尾引号括号并入句尾。
- 其他语言
  使用 `pysbd`，通过 `_split_pysbd()` 进行规则切句。

切句前后都通过 `normalize_text()` 做统一归一化。

### 5.3 句子如何映射回 span

句子映射发生在 `_map_sentences_to_segments()` 中。

处理顺序如下：

1. 把整段文本 `full_text` 由 `spans` 拼起来。
2. 为每个 span 建立字符边界区间 `(start, end)`。
3. 对每个 sentence，在 `full_text` 中从 `search_from` 开始查找位置。
4. 根据句子的字符区间调用 `_slice_spans()`，切出覆盖该句子的 span 子集。
5. 由句子首尾 span 再次计算 CFI 起止位置。
6. 为句子生成新的 `Segment`。

### 5.4 `_slice_spans()` 的作用

`_slice_spans()` 会把一句话与 span 边界做求交，得到这句对应的 span 子片段。

如果一句话只覆盖某个 span 的中间一部分，它会创建新的 `TextSpan`，并修正：

- `text`
- `char_offset`
- 继承原来的 `xpath`
- 继承原来的 `cfi_text_node_index`
- 继承原来的 `cfi_exact`

也就是说，句级 `TextSpan` 不是简单引用段落 span，而是按句子边界切出来的新 span 视图。

### 5.5 句级 CFI 的生成

当句级 span 子集拿到后，会再次调用 `generate_cfi_for_text_range()` 生成句级 `range CFI`。

因此当前实现不是：

- `paragraph CFI + sentence offset`

而是：

- 每个句子本身也有一个独立的 `range CFI`

这对后续双语句级重建更直接。

## 6. CFI 生成的内部原理

核心实现在 `bookalign/epub/cfi.py`。

### 6.1 `generate_cfi_for_text_range()`

这是 extractor 当前直接使用的 CFI 生成入口。它接收：

- `book`
- `item`
- `element`
- `start_tni`
- `start_off`
- `end_tni`
- `end_off`

其中：

- `tni` = `text_node_index`
- 坐标是“相对于段落元素的直接文本节点序列”的坐标

### 6.2 DOM 路径构建

`generate_cfi_for_text_range()` 最终调用 `_build_cfi_string()`。

`_build_cfi_string()` 先通过 `_build_dom_path(root, elem)` 计算从文档根到目标块级元素的元素路径，然后按 CFI 规则把每一级子元素索引转成偶数 step：

- 第 1 个元素子节点 -> `/2`
- 第 2 个元素子节点 -> `/4`
- 以此类推

### 6.3 包级路径

CFI 前缀中会包含：

- `/6`
  代表 package 文档中的 spine
- `/{pkg_step2}`
  代表 spine 中的某个文档项

`pkg_step2 = (spine_idx + 1) * 2`

因此，当前生成的 range CFI 结构是：

```text
epubcfi(/6/{spine-step}!{element-path},/{start-odd}:{start-off},/{end-odd}:{end-off})
```

### 6.4 文本节点步长

段落内部的直接文本节点使用奇数 step 表示：

- 文本节点 0 -> `/1`
- 文本节点 1 -> `/3`
- 文本节点 2 -> `/5`

所以：

- `start_odd = start_tni * 2 + 1`
- `end_odd = end_tni * 2 + 1`

这正是 `TextSpan` 到 CFI 坐标映射的最终落点。

## 7. CFI 解析与文本回提

当前仓库不只是“生成 CFI”，还实现了“从 CFI 回到文本”的闭环。

### 7.1 `resolve_cfi()`

`bookalign/epub/cfi.py` 中的 `resolve_cfi()` 流程是：

1. `CFIParser.parse_epubcfi()` 把 CFI 字符串解析成结构化 dict。
2. `resolve_spine_item()` 解析 package/spine 级路径，定位到具体 XHTML item。
3. `parse_item_xml()` 解析该 item 的 DOM。
4. `resolve_path()` 和 `_resolve_redirect()` 沿着 DOM step 找到目标元素/文本位置。
5. 如果是 range CFI，则分别解析 start/end，再组装为 `{'type': 'range', ...}`。

### 7.2 `extract_text_from_cfi()`

`bookalign/epub/extractor.py` 中的 `extract_text_from_cfi()` 是当前审计能力的重要接口。

它不是简单从原始文本节点直接切字符串，而是：

1. 先 `resolve_cfi(cfi, book)`。
2. 确认 start/end 都成功解析，并且目前要求落在同一个父节点。
3. 对该父节点再次执行 `_collect_text_spans()`，也就是再次按“当前正文抽取规则”生成 span。
4. 调用 `_extract_text_from_spans()`，根据 CFI 边界从这些 span 中恢复可读文本。

这意味着当前回提文本与 extractor 主逻辑共享同一套过滤规则，而不是另起一套“解析规则”。

### 7.3 当前回提的边界

`extract_text_from_cfi()` 当前有一个明确限制：

- 只处理 start 和 end 落在同一个父节点的 range。

这与当前 extractor 生成的段落/句子 segment 是一致的，因为 segment 本来就是围绕单个块级元素生成的。

仓库里也有更通用的 `extract_range_text()`，它支持跨节点范围提取，但当前 extractor 的主验证路径没有直接用它。

## 8. 测试现在是怎么做的

当前文本抽取相关测试主要分两类。

## 8.1 分句单元测试

文件：`tests/test_splitter.py`

当前覆盖：

- 日文
- 中文
- 英文
- 西班牙文

测试重点：

- 核心句末标点与引号处理是否正确
- `split()` 后重新拼接并归一化，是否能回到原始规范化文本

这部分主要验证句边界逻辑，不涉及 EPUB。

## 8.2 真实 EPUB 集成测试

文件：`tests/test_extractor.py`

这是目前最关键的测试。

### 8.2.1 测试样本来源

测试会从仓库 `books/` 目录中的真实 EPUB 中取样，目前覆盖：

- `ja`: `kinkaku.epub`
- `en`: `*Sherlock Holmes*.epub`
- `es`: `Don Quijote*.epub`
- `zh`: `her.epub`

### 8.2.2 抽样方式

测试使用固定随机种子：

- `RNG_SEED = 20260314`

并在每本书中：

1. 按 spine 获取文档
2. 用 XPath `COMPLEX_NODE_XPATH` 查找“带内联结构且长度足够”的复杂段落候选
3. 每本书随机选若干章节和段落

这里 XPath 的用途只是“测试样本发现”，不是生产抽取主流程。

### 8.2.3 核心断言

对每个样本节点，测试会同时跑：

- 段落级抽取：`extract_segments(..., splitter=None)`
- 句子级抽取：`extract_segments(..., splitter=SentenceSplitter(language))`

并验证：

1. 目标段落能在 extractor 结果中找到。
2. `paragraph_segment.cfi` 是合法的 `epubcfi(...)`。
3. `paragraph_segment.spans` 不为空。
4. `''.join(span.text for span in paragraph_segment.spans) == paragraph_segment.text`
5. 段落文本等于按测试辅助规则计算的 `expected_text`
6. 文本中不包含 HTML 标签、换行制表符、连续多空格等脏模式
7. `resolve_cfi(paragraph_segment.cfi, book)` 能成功解析
8. `extract_text_from_cfi(book, paragraph_segment.cfi, config=config)` 能回提文本
9. 句子级结果重新拼接后，应等于原段落文本
10. 所有句子 segment 也都必须有合法 CFI

### 8.2.4 审计产物

测试还会把样本写到：

- `tests/artifacts/epub_extraction_audit.jsonl`

每条记录包含：

- language
- book
- chapter_idx
- doc_name
- cfi
- raw_html_excerpt
- paragraph_text
- sentences

这个文件的作用是人工抽查当前 extractor 在真实书籍上的表现。

## 9. 关键函数索引

如果要快速进入实现，优先看这些函数。

### 9.1 读取与文档枚举

- `bookalign/epub/reader.py`
  - `read_epub()`
  - `get_spine_documents()`

### 9.2 标签过滤

- `bookalign/epub/tag_filters.py`
  - `should_skip_element()`
  - `is_block_element()`
  - `is_structural_container()`

### 9.3 抽取主链

- `bookalign/epub/extractor.py`
  - `extract_segments()`
  - `_collect_text_spans()`
  - `_iter_readable_text_parts()`
  - `_trim_spans()`
  - `_map_sentences_to_segments()`
  - `_slice_spans()`
  - `extract_text_from_cfi()`

### 9.4 CFI 主链

- `bookalign/epub/cfi.py`
  - `parse_item_xml()`
  - `generate_cfi_for_text_range()`
  - `resolve_cfi()`
  - `resolve_path()`
  - `resolve_dom_steps()`
  - `resolve_text_pos()`
  - `_build_cfi_string()`

### 9.5 分句

- `bookalign/epub/sentence_splitter.py`
  - `SentenceSplitter.split()`
  - `SentenceSplitter.normalize_text()`
  - `SentenceSplitter._split_cjk()`
  - `SentenceSplitter._split_pysbd()`

## 10. 当前实现的实际特点与边界

当前方案已经形成一条稳定主链，但仍有明确边界。

### 10.1 已经成立的能力

- 可以按 spine 顺序读取真实 EPUB 文档。
- 可以过滤注音、脚注引用、目录和结构包装器。
- 可以抽出用于对齐的干净段落文本。
- 可以在段落级和句子级生成 `range CFI`。
- 可以从生成出的 CFI 再回提文本做验证。
- 已有基于真实多语言 EPUB 的集成测试。

### 10.2 当前实现的折中

- 对于内联子元素内部文本，当前 CFI 采用“吸附到父元素文本节点边界”的方式，而不是给每个子节点内部字符建立完全精确的 CFI 坐标。
- 这是一种面向稳定性和可实现性的折中，重点是保证段落/句子的可追踪范围和抽取一致性。

### 10.3 目前仍有限制的点

- `extract_text_from_cfi()` 当前主要处理同一父节点内的 range。
- 句子映射依赖 `full_text.find(sentence, search_from)`，如果分句结果和归一化后文本出现复杂不一致，存在找不到句子位置的风险。
- 复杂 EPUB 的特殊结构仍可能需要按书籍扩展 `TagFilterConfig`。
- 目前 builder/aligner 尚未进入完整实现，因此当前文档只覆盖“抽取与定位”，不覆盖双语重建。

## 11. 一句话总结

当前项目从 EPUB 中抽取对齐文本的实现，可以概括为：

先以块级元素为单位，结合标签过滤抽出可读文本和 `TextSpan`，再把这些文本映射成段落级或句子级 `range CFI`；其中 `CFI` 是主定位机制，`XPath` 主要用于调试和测试审计；并通过 `resolve_cfi() + extract_text_from_cfi()` 与真实 EPUB 集成测试形成闭环验证。
