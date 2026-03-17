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
- `sentence_splitter.py` 已覆盖 `ja/zh/en/es`
- `cfi.py` 已支持句段级 range CFI 生成与回提
- `Segment` 已补齐 `paragraph_cfi`、`text_start`、`text_end`

### 对齐

- 已接入 `BertalignAdapter`
- 已实现章节级 DP 匹配
- 已支持 `structured` / `raw` 两种章节匹配模式
- 《金阁寺》上已验证 `structured` 能避开前后附文错配
- 已支持将 `AlignmentResult` 存储为 JSON，用于后续 builder-only 测试

### EPUB builder

- `simple` builder 可生成句对式双语 EPUB
- `source_layout` builder 可基于 source `CFI` 把译文回写到原书结构
- `source_layout` 已拆成 `writeback_mode=paragraph|inline`
- source-layout 默认输出中文横排版本
- 已修复部分阅读器中由原书 `rtl` 方向继承导致的翻页颠倒问题
- 已修复 source-layout 输出 XHTML 的可读性和调试可读性
- `inline` 模式已支持在原 block 内按“原句 -> 译句”交错回写，并在段与段之间插入空白分隔段

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
37 passed in 69.42s
```

当前环境已经确认：

- `uv` 开发环境可用
- `align` 依赖组可用
- `/root/model/LaBSE` 可作为本地模型路径
- bertalign 运行时可加载本地模型

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
3. 为缓存 alignment JSON 的 builder 回归建立更系统的抽样基线。
4. 扩展真实书籍覆盖，不只依赖《金阁寺》单一主样本。
