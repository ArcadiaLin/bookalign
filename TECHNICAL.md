# BookAlign 技术说明

## 1. 总览

BookAlign 当前正式 pipeline 只有一条：

```text
source EPUB + target EPUB
-> filtered_preserve extraction
-> structured chapter matching
-> Bertalign sentence alignment
-> bilingual EPUB build
```

这条 pipeline 的核心目标是：

- 正文尽量稳定参与对齐
- 目录、注释、前后附文等非正文不在抽取阶段丢弃
- builder 仍能把保留信息回写到输出书里

## 2. 核心数据结构

### 2.1 `Segment`

定义位置：

- `bookalign/models/types.py`

关键字段：

- `text`: 当前句段文本
- `cfi`: 句子级或段落级 range CFI
- `paragraph_cfi`: 所属段落锚点
- `chapter_idx / paragraph_idx / sentence_idx`: 结构位置
- `text_start / text_end`: 句子在段落规范化文本中的范围
- `raw_html`: 原始块级 HTML
- `element_xpath`: 调试用 XPath
- `has_jump_markup / is_note_like / jump_fragments`: 注释跳转与脚注元数据
- `alignment_role`: `align | retain`
- `paratext_kind`: `body | toc | note_body | chapter_heading | frontmatter | backmatter | metadata | unknown`
- `filter_reason`: 启发式分类原因

职责：

- 作为 Bertalign 的输入文本单元
- 作为 builder 回写的最小定位单元
- 作为 JSON 缓存中的稳定中间表示

### 2.2 `AlignmentResult`

关键字段：

- `pairs`: 对齐后的 `AlignedPair[]`
- `source_lang / target_lang`
- `granularity`
- `extract_mode`
- `retained_source_segments / retained_target_segments`

`retained_*` 的作用：

- 正文不参与对齐的非正文段不会丢失
- builder 可以在 `filtered_preserve` 下把 target retained segment 统一写入附录

## 3. 模块职责

### 3.1 `bookalign/epub/reader.py`

职责：

- 读取 EPUB
- 获取 spine 文档

常用接口：

- `read_epub(path)`
- `get_spine_documents(book)`

### 3.2 `bookalign/epub/tag_filters.py`

职责：

- 提供 `filtered_preserve` 专用的元素抽取策略
- 决定哪些节点被保留文本、哪些节点被跳过、哪些节点只保留子文本

当前只支持：

- `build_tag_filter_config('filtered_preserve')`

### 3.3 `bookalign/epub/extractor.py`

职责：

- 从单个 XHTML 文档中提取 paragraph/sentence `Segment`
- 生成 CFI、句内偏移与 jump metadata
- 给每个 segment 打上 `alignment_role / paratext_kind / filter_reason`

公开接口：

```python
extract_segments(
    book,
    doc,
    chapter_idx,
    *,
    config=None,
    splitter=None,
    extract_mode='filtered_preserve',
) -> list[Segment]
```

当前抽取语义：

- `paratext_kind == 'body'` 的 segment 标记为 `alignment_role='align'`
- 其余命中的目录、脚注、章节标题、前后附文等标记为 `alignment_role='retain'`

### 3.4 `bookalign/epub/sentence_splitter.py`

职责：

- 多语言分句
- 处理 CJK 引号、繁中兼容引号、书名号、括号等细节

当前已覆盖：

- `ja`
- `zh`
- `en`
- `es`

### 3.5 `bookalign/epub/cfi.py`

职责：

- 生成段落级和句子级 CFI
- 从 CFI 回提文本
- 为 builder 提供稳定锚点

### 3.6 `bookalign/align/*`

职责：

- 封装对齐后端
- 当前正式使用 `BertalignAdapter`

`BaseAligner` 输出的 bead 允许：

- `1-1`
- `1-N`
- `N-1`
- `N-M`
- `1-0 / 0-1`

### 3.7 `bookalign/pipeline.py`

职责：

- 串联抽取、章节匹配、句子对齐、builder

关键接口：

```python
extract_sentence_chapters(book, *, language: str, extract_mode: str = 'filtered_preserve') -> list[ExtractedChapter]
match_extracted_chapters(source_chapters, target_chapters, *, chapter_match_mode: str = 'structured') -> list[ChapterMatch]
align_books(source_book, target_book, *, source_lang: str, target_lang: str, chapter_match_mode: str | None = None, extract_mode: str = 'filtered_preserve', aligner: BaseAligner | None = None, enable_local_realign: bool = False) -> AlignmentResult
run_bilingual_epub_pipeline(*, source_epub_path, target_epub_path, output_path, source_lang='ja', target_lang='zh', builder_mode='simple', chapter_match_mode=None, extract_mode='filtered_preserve', alignment_json_input_path=None, alignment_json_output_path=None, writeback_mode='paragraph', layout_direction='horizontal', emit_translation_metadata=False, normalize_vertical_punctuation=True, aligner=None, enable_local_realign=False) -> AlignmentResult
build_bilingual_epub_from_alignment_json(*, source_epub_path, target_epub_path, alignment_json_path, output_path, builder_mode='simple', writeback_mode='paragraph', layout_direction='horizontal', emit_translation_metadata=False, normalize_vertical_punctuation=True, extract_mode='filtered_preserve') -> AlignmentResult
```

### 3.8 `bookalign/alignment_json.py`

职责：

- 把 `AlignmentResult` 保存为 JSON
- 从 JSON 恢复 `AlignmentResult`
- 提供 builder-only 测试入口

## 4. 当前正式 pipeline 的工作原理

### 4.1 抽取

`extract_sentence_chapters()` 会遍历每个可读 spine 文档，并调用 `extract_segments(...)`。

每个 `ExtractedChapter` 同时保留三份视图：

- `segments`: 全部 segment
- `alignment_segments`: 只含 `alignment_role='align'` 的正文
- `retained_segments`: 只含 `alignment_role='retain'` 的非正文

### 4.2 章节匹配

`match_extracted_chapters()` 使用顺序 DP，在 source/target 章节序列上寻找最低代价路径。

默认使用：

- `chapter_match_mode='structured'`

当前仍保留：

- `chapter_match_mode='raw'`

但 `raw` 只建议用于局部诊断，不再是正式 pipeline 的主轴配置。

### 4.3 句子对齐

`align_books()` 会把每个 matched chapter 的 `alignment_segments` 喂给 Bertalign。

这意味着：

- 正文参与对齐
- retained segment 不参与对齐
- retained segment 仍会保存在 `AlignmentResult` 中

### 4.4 局部重对齐

如果启用 `enable_local_realign=True`，pipeline 会在章节内扫描疑似断链窗口。

当前策略：

1. 先用正常参数完成整章对齐
2. 在正文区扫描异常窗口
3. 对命中的窗口用更激进的保守参数局部重对齐
4. 再从修复边界开始对后缀重跑一次原始参数
5. 只有新结果更好时才替换原窗口/后缀

这套逻辑主要是为《假面的告白》繁中的正文中段断链问题准备的。

## 5. Builder 设计

### 5.1 `simple`

特点：

- 新建 XHTML 页面
- 按章节写入 source/target 句对
- 最适合查对对齐质量

### 5.2 `source_layout`

特点：

- 保留 source 的 spine 顺序和 XHTML 文件结构
- 保留原始 `<head>` 中的标题和样式链接
- 通过 CFI 回到原文档做回写

#### `writeback_mode='paragraph'`

- 按 source paragraph 聚合同段译文
- 在原段落后插入一个译文 `<p>`
- 结构最稳，适合作为保底路径

#### `writeback_mode='inline'`

- 保留原始 block 容器
- 在段内按“原句 -> 译句”交错回写
- 段内只插 `<br/>`
- 段间插入 `<p><br/></p>`
- builder 会重新收集 live DOM 文本轨迹，再按 `text_start/text_end` 切句

### 5.3 `filtered_preserve` 的附录回写

当前 builder 会把 target retained segment 写入一个 synthetic XHTML：

- `xhtml/bookalign-retained-target.xhtml`

这个附录的作用：

- 承载目录、注释、前后附文等 retained 内容
- 让正文注释引用有稳定的跳转目标
- 让附录中的 backlink 可以指回正文里的新锚点

## 6. 跳转与注释保留

`jump_fragments` 保存的是 builder 重写跳转所需的最小结构化信息。

当前 builder 会维护两张映射：

- `note_anchor_map`
  - 原 note id -> 附录中的新 note id
- `note_ref_anchor_map`
  - 原 note id -> 正文中的新 note ref id

最终效果：

- 正文 note ref -> 跳到附录中的 note body
- 附录 note body 的 backlink -> 跳回正文中的 note ref

## 7. 横排兼容策略

当 `layout_direction='horizontal'` 时：

- builder 会注入横排覆盖 CSS
- 统一改成左对齐
- 取消默认首行缩进
- 输出书方向设为 `ltr`
- 译文文本会做竖排符号到横排符号的归一化

这样做是为了避免：

- 继承原日文 `rtl` 阅读方向
- 某些阅读器分页方向倒置
- 繁中竖排兼容标点在横排书里继续出现

## 8. 当前已知问题

### 8.1 《假面的告白》繁中断链

当前最明确的问题是《假面的告白》繁中在正文中段仍存在少量疑似断链窗口。

典型信号：

- 前面先有稳定 `1-1`
- 随后突然出现连续 `4-1/1-4`
- 中间夹 `1-0/0-1`
- 句长比极端失衡

这类问题已经不是 builder 可以修复的，而是对齐结果层的问题。

### 8.2 边界 skip 不等于坏对齐

书头/书尾的连续 `0-1/1-0` 很多时候只是：

- 导读
- 版权
- 目录
- 译者附文

这类 skip 不应直接判为断链。

## 9. 推荐调用方式

### 9.1 端到端

```bash
uv run bookalign SOURCE.epub TARGET.epub OUTPUT.epub \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode inline \
  --layout-direction horizontal
```

### 9.2 先生成 JSON，再做 builder-only 回归

```bash
uv run python -m bookalign.cli SOURCE.epub TARGET.epub OUT.epub \
  --builder-mode source_layout \
  --writeback-mode inline \
  --alignment-json-output alignment.json
```

```bash
uv run python -m bookalign.cli SOURCE.epub TARGET.epub OUT.epub \
  --builder-mode source_layout \
  --writeback-mode inline \
  --alignment-json-input alignment.json
```

## 10. 当前建议

当前最值得继续投入的方向：

1. 继续收敛《假面的告白》繁中的局部断链窗口。
2. 继续增强 `filtered_preserve` 附录跳转在不同阅读器中的稳定性。
3. 继续扩大 inline 回写的真实书回归。
4. 继续把 builder 调整建立在 alignment JSON 复用上，而不是保留大量真实书产物到仓库中。
