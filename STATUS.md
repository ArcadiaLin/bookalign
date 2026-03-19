# BookAlign 当前状态

## 总体状态

项目已从“抽取能力开发中”进入“端到端主链路可运行”阶段。

当前可运行链路：

```text
EPUB 读取
-> 句子级 Segment 抽取
-> 章节匹配
-> Bertalign 句子对齐
-> 双语 EPUB 输出
```

这条链路已经在《金阁寺》日文原版与中文译本上实际跑通。

## 已完成

### 抽取与定位

- `reader.py` 已稳定按 spine 读取 XHTML
- `extractor.py` 已稳定输出 paragraph/sentence `Segment`
- 抽取已拆成三条主轴：`extract_mode=filtered|full_text|filtered_preserve`
- `sentence_splitter.py` 已覆盖 `ja/zh/en/es`
- `cfi.py` 已支持句段级 range CFI 生成与回提
- `Segment` 已补齐 `paragraph_cfi`、`text_start`、`text_end`
- `Segment` 已补齐 `has_jump_markup`、`is_note_like`、`jump_fragments`
- `Segment` 已补齐 `alignment_role`、`paratext_kind`、`filter_reason`

### 对齐

- 已接入 `BertalignAdapter`
- 已实现章节级 DP 匹配
- 已支持 `structured` / `raw` 两种章节匹配模式
- 《金阁寺》上已验证 `structured` 能避开前后附文错配
- `full_text` 主轴默认与 `raw` 章节匹配配套使用
- `filtered_preserve` 主轴默认与 `structured` 章节匹配配套使用，并把 target 非正文写入单独的 `译文附录`
- 已支持将 `AlignmentResult` 存储为 JSON，用于后续 builder-only 测试

### EPUB builder

- `simple` builder 可生成句对式双语 EPUB
- `source_layout` builder 可基于 source `CFI` 把译文回写到原书结构
- `source_layout` 已拆成 `writeback_mode=paragraph|inline`
- source-layout 默认输出中文横排版本
- 已修复部分阅读器中由原书 `rtl` 方向继承导致的翻页颠倒问题
- 已修复 source-layout 输出 XHTML 的可读性和调试可读性
- `inline` 模式已支持在原 block 内按“原句 -> 译句”交错回写，并在段与段之间插入空白分隔段
- `full_text` 主轴下已支持 target 注释跳转与译注正文保留
- `filtered_preserve` 主轴下已支持“正文参与对齐、非正文保留回写”的混合链路
- 未匹配的 target 注释类 segment 会追加到最后一章末尾

### 测试与审阅

- `pytest` 主测试集已覆盖 extractor / splitter / aligner / pipeline / builder
- `debug_report.py` 可生成 Markdown 审阅报告
- 提交中保留 `tests/artifacts/batch_reader_reports/` 作为人工审阅样本

## 当前默认工作流

### 调试句对

优先使用：

- `builder_mode=simple`

原因：

- 句对结构清晰
- 便于快速发现对齐错误
- 不受原书版式和阅读器差异影响

### 调试原书回写

优先使用：

- `builder_mode=source_layout`
- `writeback_mode=inline`
- `layout_direction=horizontal`

原因：

- 保留 source 章节结构
- 中文阅读器兼容性更好
- 可直接观察句位回写效果
- 当前是更适合人工审阅的实际输出模式

## 当前边界

- `paragraph` 模式仍是更稳的默认回写路径
- `inline` 模式当前主要面向日文 source EPUB
- `raw` 章节匹配主要用于对照测试，不是默认推荐模式
- 对齐得分目前仍是 adapter 默认分值，不是严格语义置信度
- builder 的样式保真仍以“可读”和“兼容”优先，不追求完全复制原书视觉

## 已验证状态

最近一次全量测试：

```text
62 passed in 74.00s
```

当前环境已经确认：

- `uv` 开发环境可用
- `align` 依赖组可用
- `/root/model/LaBSE` 可作为本地模型路径
- bertalign 运行时可加载本地模型

## 当前 JSON 分布观察

基于 `tests/artifacts/extract_*/` 下现有真实书 JSON 的人工与脚本复核，当前对齐质量可分成两类：

- 整体健康：
  - `extract_filtered/金阁寺-繁中-对齐结果.json`
  - `extract_filtered/金阁寺-简中-对齐结果.json`
  - `extract_filtered/假面的告白-简中-对齐结果.json`
- 明显存在正文中段断链风险：
  - `extract_filtered/假面的告白-繁中-对齐结果.json`
  - `extract_full_text/假面的告白-繁中-对齐结果.json`
  - `extract_filtered_preserve/假面的告白-繁中-对齐结果.json`
  - `extract_full_text/金阁寺-繁中-对齐结果.json`

当前已确认的典型分布特征：

- 健康样本通常以 `1-1` 为主，`skip(1-0/0-1)` 与大 bead (`4-1/1-4/...`) 占比较低。
- 《假面的告白》繁中三条主轴的 `1-1` 占比都只有约 `56%~59%`，`skip` 约 `20%~25%`，大 bead 约 `13%~15%`。
- `full_text/金阁寺-繁中` 最差，`1-1` 仅约 `14.8%`，`skip` 约 `38.3%`，大 bead 约 `34.5%`，已经接近整体失控。

## 当前断链判断

现阶段可以明确区分两类 skip：

- 无害 skip：
  - 典型如 `extract_filtered/金阁寺-繁中-对齐结果.json` 开头 `0..45` 的连续 `0-1`
  - 本质是译者导读、版权或前后附文
  - 发生在边界，且紧接着能恢复到稳定正文对齐
- 异常断链：
  - 发生在正文中段
  - 前面往往先有稳定 `1-1`
  - 之后突然出现连续 `4-1/1-4`、`1-0/0-1`
  - 常伴随极端长度比失衡
  - 《假面的告白》繁中的“汽車が走り出さない...”一段就是这种情况

当前脚本扫描显示：

- `extract_filtered/金阁寺-繁中` 在排除边界区后没有明显异常窗口
- `extract_filtered_preserve/假面的告白-繁中` 存在多处正文异常窗口，例如 `[1710,1768]`、`[1825,1860]`、`[1939,2015]`、`[2028,2169]`

## 当前建议方案

当前最值得实现的不是整本重跑，而是“断链窗口检测 + 局部重对齐”：

- 在正文区按顺序扫描滑窗
- 结合 `skip`、大 bead、极端长度比、前置稳定区来标记疑似断链
- 对命中的局部窗口单独重对齐
- 重对齐时收紧 `max_align`，提高 skip 代价，保留长度惩罚
- 只有当局部 `1-1` 占比上升、`skip/big bead` 下降时才替换原窗口结果

## 当前仓库整理状态

为了后续提交，当前已完成一次仓库清理：

- 删除了根目录下过时 extraction 文档
- 新增统一技术说明文档 `TECHNICAL.md`
- 清理了 `tests/artifacts/` 中大部分生成物
- 仅保留 `tests/artifacts/batch_reader_reports/`
- 收紧了 `.gitignore`，避免新生成物再次进入提交

## 下一步

1. 继续提升 source-layout 在不同阅读器中的兼容性。
2. 继续扩大 inline 回写在真实书上的样式与阅读器回归覆盖。
3. 继续收敛 `full_text` 主轴下目录/注释参与对齐后的质量边界。
4. 为缓存 alignment JSON 的 builder 回归建立更系统的抽样基线。
