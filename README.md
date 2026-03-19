# BookAlign

BookAlign 用于把原版 EPUB 与译本 EPUB 做句子级抽取、双语对齐，并重建为可阅读的双语 EPUB。

当前项目已经收口为一条正式 pipeline：

```text
source EPUB + target EPUB
-> filtered_preserve extraction with CFI anchors
-> structured chapter matching
-> Bertalign sentence alignment
-> bilingual EPUB build
```

这条 pipeline 的目标是同时满足两件事：

- 正文对齐尽量稳，不让目录、导读、注释正文直接拖坏后文对齐
- 被识别出来的非正文信息不在抽取阶段丢弃，而是保留下来供 builder 回写

## 当前能力

### 1. EPUB 抽取

- 按 spine 顺序读取正文 XHTML
- 在 paragraph 基础上继续切成句子级 `Segment`
- 为段落和句子生成可回溯的 `CFI`
- 抽取时保留 `alignment_role / paratext_kind / filter_reason`
- 正文进入对齐，目录/注释/前后附文进入 retained 流程

### 2. 双语对齐

- `BertalignAdapter` 封装 vendored `bertalign`
- 默认使用 `structured` 章节匹配
- 支持把 `AlignmentResult` 保存为 JSON，供 builder-only 回归复用
- 支持可选的断链窗口检测与局部重对齐

### 3. EPUB 构建

- `simple`：生成新的句对式双语 EPUB
- `source_layout --writeback-mode paragraph`：保留 source 结构，在原段后写回译文
- `source_layout --writeback-mode inline`：在原 block 内按“原句 -> 译句”交错回写
- `filtered_preserve` 模式下会额外生成 `译文附录` XHTML
- 正文内注释跳转会重写到附录中的真实锚点
- 横排输出会同时修正 CSS 和书级阅读方向，避免部分阅读器分页反转

## 当前边界

- `paragraph` 仍是更稳的默认回写模式
- `inline` 主要面向日文 source EPUB
- 复杂诗排、图文页、极差 EPUB 的兼容仍需继续补
- 《假面的告白》繁中仍存在少量正文中段断链窗口，需要继续收敛

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
tests/artifacts/    # 本地生成目录；提交中只保留 batch_reader_reports
```

## 环境

- Python `3.12`
- 包管理器 `uv`
- 对齐运行时依赖位于 `align` 依赖组
- 本地 LaBSE 模型路径优先使用 `/root/model/LaBSE`

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
  out.epub \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode inline \
  --layout-direction horizontal
```

输出简单句对版：

```bash
uv run bookalign \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  out-simple.epub \
  --source-lang ja \
  --target-lang zh \
  --builder-mode simple
```

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
