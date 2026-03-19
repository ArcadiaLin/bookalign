# BookAlign

BookAlign 用于把原版 EPUB 与译本 EPUB 做句子级抽取、双语对齐，并重建为可阅读的双语 EPUB。

当前主链路已经可运行：

```text
source EPUB + target EPUB
-> sentence-level extraction with CFI anchors
-> chapter matching
-> Bertalign sentence alignment
-> bilingual EPUB build
```

项目当前重点已经从 extractor 单点验证推进到完整工程链路，尤其是：

- 基于 `Segment` 的句子级对齐
- 基于 `CFI` 的 source-layout 回写
- 三条 extractor 主轴：`filtered` / `full_text` / `filtered_preserve`
- 双 builder 模式
- 《金阁寺》日文原版 / 中文译本真实书籍验证

## 当前能力

### 1. EPUB 读取与抽取

- 按 spine 顺序读取正文 XHTML
- 基于规则和策略抽取可读段落
- 支持 `extract_mode=filtered|full_text|filtered_preserve`
- 在段落上继续切成句子级 `Segment`
- 为段落和句子生成可回溯的 `CFI`

### 2. 双语对齐

- `BertalignAdapter` 封装 vendored `bertalign`
- 章节级 DP 匹配，避免原书/译本 frontmatter 直接错配
- 支持 `structured` 和 `raw` 两种章节匹配模式
- `full_text` 主轴默认配合 `raw` 章节匹配，允许目录/注释参与对齐
- `filtered_preserve` 主轴默认配合 `structured`，对齐时只用正文，但会保留被过滤出的目录/注释/前后附文
- 支持把 `AlignmentResult` 保存为 JSON，供后续 builder-only 回归复用

### 3. EPUB 构建

- `simple` 模式：生成新的双语对照书
- `source_layout --writeback-mode paragraph`：保留 source XHTML 结构，在原段落后写回译文
- `source_layout --writeback-mode inline`：保留 source block 容器，在段内按“原句 -> 译句”交错回写
- `source_layout + horizontal` 模式下，会把输出书的阅读方向改为 `ltr`，避免部分阅读器沿用原日文 `rtl` 翻页语义
- `full_text` 主轴下，target 注释跳转与注释正文会进入对齐和回写
- `filtered_preserve` 主轴下，target 非正文内容不会参与对齐，但会写入单独的 `译文附录` XHTML，并重写正文注释跳转

## 当前边界

- `inline` 模式当前优先覆盖日文 source 书籍
- 对极复杂 inline 结构仍以“合法 XHTML + 可读 + 尽量保留 inline”为优先，不保证完全视觉等价
- 章节匹配仍以结构和启发式为主，不是跨章语义全局优化
- 对复杂诗排、图文页、极差 EPUB 的兼容还不完整

## 目录结构

```text
bookalign/
├── align/          # 对齐抽象与 bertalign 适配
├── epub/           # 读取、CFI、抽取、builder、审阅报告
├── models/         # Segment / AlignmentResult 等共享数据模型
├── cli.py          # CLI 入口
└── pipeline.py     # 端到端编排

books/              # 本地测试用 EPUB
scripts/            # 环境准备和运行时 smoke test
tests/              # pytest
tests/artifacts/    # 生成目录；当前真实书结果按 extract_filtered/extract_full_text/extract_filtered_preserve 分目录
```

## 环境

- Python `3.12`
- 包管理器 `uv`
- 对齐运行时依赖位于 `align` 依赖组
- 本地 LaBSE 模型路径当前优先使用 `/root/model/LaBSE`

## 安装

基础开发环境：

```bash
uv sync --group dev
```

含对齐运行时：

```bash
uv sync --group dev --group align
```

## 常用命令

运行测试：

```bash
uv run pytest
```

快速验证抽取：

```bash
uv run pytest tests/test_splitter.py tests/test_extractor.py -q
```

查看 debug report CLI：

```bash
uv run python -m bookalign.epub.debug_report --help
```

运行端到端双语 EPUB：

```bash
uv run bookalign \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  tests/artifacts/kinkaku_ja_zh_source_layout.epub \
  --source-lang ja \
  --target-lang zh \
  --extract-mode filtered \
  --builder-mode source_layout \
  --writeback-mode inline \
  --layout-direction horizontal
```

输出简单句对版：

```bash
uv run bookalign \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  tests/artifacts/kinkaku_ja_zh_simple.epub \
  --source-lang ja \
  --target-lang zh \
  --builder-mode simple
```

## 验证状态

当前主链路已经在《金阁寺》原文/译本上真实跑通，并完成过以下验证：

- 章节匹配可避开前后附文
- Bertalign 实际产出句对
- `simple` 和 `source_layout` 两种 builder 均可生成 EPUB
- `source_layout` 横排输出已修复阅读方向和分页兼容性问题
- `source_layout` 已支持 `paragraph` / `inline` 两种回写策略
- 当前真实书结果按 `tests/artifacts/extract_filtered/`、`tests/artifacts/extract_full_text/`、`tests/artifacts/extract_filtered_preserve/` 分目录保存

最新测试状态见 `STATUS.md`。

## 文档

- `README.md`: 项目总览与上手
- `DESIGN.md`: 架构与设计决策
- `STATUS.md`: 当前进度、验证状态、下一步
- `TECHNICAL.md`: 详细技术说明，包含接口、数据结构、流程和原理
- `TESTING.md`: 测试调用方式、参数和 JSON 复用流程

## 提交与产物策略

- `books/` 视为本地测试材料，不新增大体积书籍
- `tests/artifacts/` 默认不提交生成物
- 当前保留的提交级人工审阅产物只有 `tests/artifacts/batch_reader_reports/`
