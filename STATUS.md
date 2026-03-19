# BookAlign 当前状态

## 总体状态

项目已经从多主轴实验阶段收口到单一正式 pipeline：

```text
EPUB 读取
-> filtered_preserve sentence extraction
-> structured chapter matching
-> Bertalign sentence alignment
-> bilingual EPUB build
```

`filtered` 与 `full_text` 两条实验主轴已移除，不再作为项目对外工作流保留。

## 已完成

### 抽取与定位

- `reader.py` 已稳定按 spine 读取 XHTML
- `extractor.py` 已稳定输出 paragraph/sentence `Segment`
- 当前只保留 `extract_mode='filtered_preserve'`
- `sentence_splitter.py` 已覆盖 `ja/zh/en/es`
- `cfi.py` 已支持句段级 range CFI 生成与回提
- `Segment` 已补齐 `paragraph_cfi`、`text_start`、`text_end`
- `Segment` 已补齐 `has_jump_markup`、`is_note_like`、`jump_fragments`
- `Segment` 已补齐 `alignment_role`、`paratext_kind`、`filter_reason`

### 对齐

- 已接入 `BertalignAdapter`
- 已实现章节级 DP 匹配
- 默认章节匹配为 `structured`
- 已支持将 `AlignmentResult` 存储为 JSON，用于 builder-only 回归
- 已支持可选的“断链窗口检测 + 局部重对齐”后处理

### EPUB builder

- `simple` builder 可生成句对式双语 EPUB
- `source_layout` builder 可基于 source `CFI` 回写到原书结构
- `source_layout` 支持 `writeback_mode=paragraph|inline`
- 默认输出中文横排版本
- 已修复部分阅读器中由原书 `rtl` 方向继承导致的翻页颠倒问题
- `filtered_preserve` 下，target 非正文会写入单独的 `译文附录`
- builder 已支持正文 note ref 与附录 note body/backlink 的双向改写

### 测试与审阅

- `pytest` 主测试集已覆盖 extractor / splitter / aligner / pipeline / builder
- `debug_report.py` 可生成 Markdown 审阅报告
- 提交中仅保留 `tests/artifacts/batch_reader_reports/` 作为人工审阅样本
- 旧的真实书 JSON/EPUB 结果目录已清理，不再作为仓库基线保留

## 当前默认工作流

### 调试句对

优先使用：

- `builder_mode=simple`

### 调试原书回写

优先使用：

- `builder_mode=source_layout`
- `writeback_mode=inline`
- `layout_direction=horizontal`

## 当前边界

- `paragraph` 仍是更稳的默认回写路径
- `inline` 模式当前主要面向日文 source EPUB
- `raw` 章节匹配仍只建议作为局部诊断参数，不再是正式主轴的一部分
- 对齐得分目前仍是 adapter 默认分值，不是严格语义置信度
- builder 的样式保真仍以“可读”和“兼容”优先，不追求完全复制原书视觉

## 当前问题观察

历史真实书验证表明，真正需要继续收敛的是《假面的告白》繁中这组结果的正文中段断链，而不是再维护多套 extract 主轴。

目前已确认：

- 边界区的大段 `0-1/1-0` 往往只是导读、版权、目录或译者附文，不一定会破坏后文对齐。
- 真正危险的是正文中段突然出现“稳定 `1-1` -> 连续 `4-1/1-4` -> `1-0/0-1` -> 持续漂移”的模式。
- 这类问题已经通过 `enable_local_realign` 获得初步收敛，但仍有残余窗口需要继续分析。

## 当前建议方案

当前最值得继续投入的是：

1. 继续收敛《假面的告白》繁中的局部断链窗口。
2. 继续验证 `filtered_preserve` 下附录跳转与正文回跳在不同阅读器中的稳定性。
3. 继续扩大 inline 回写在真实书上的样式与阅读器回归覆盖。
4. 继续使用 alignment JSON 做 builder-only 回归，而不是把真实书产物留在仓库里。
