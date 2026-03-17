# BookAlign 测试与调用说明

本文档集中说明当前项目里与抽取、对齐、builder 回归相关的常用调用方式、参数和推荐用法。

## 1. 基础测试

全量测试：

```bash
uv run pytest -q
```

抽取主链路：

```bash
uv run pytest tests/test_splitter.py tests/test_extractor.py -q
```

builder / pipeline：

```bash
uv run pytest tests/test_builder.py tests/test_pipeline.py -q
```

真实 EPUB 集成测试：

```bash
uv run pytest -m integration -q
```

## 2. 直接运行对齐并构建 EPUB

这是最完整的链路：抽取、章节匹配、Bertalign、builder 全部重跑。

示例：

```bash
UV_CACHE_DIR=/tmp/uv-cache \
PYTHONPATH=. \
HF_HOME=/root/projs/bookalign/.cache/huggingface \
SENTENCE_TRANSFORMERS_HOME=/root/projs/bookalign/.cache/huggingface \
TRANSFORMERS_CACHE=/root/projs/bookalign/.cache/huggingface/transformers \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run python -m bookalign.cli \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  "tests/artifacts/金阁寺-句子级回写.epub" \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode inline \
  --chapter-match-mode structured \
  --layout-direction horizontal
```

关键参数：

- `--builder-mode simple|source_layout`
- `--writeback-mode paragraph|inline`
- `--chapter-match-mode structured|raw`
- `--layout-direction horizontal|source`
- `--emit-translation-metadata`

## 3. 先保存对齐结果，再做 builder 回归

这是后续 builder 测试的推荐路径。第一次运行时保存 Bertalign 结果；后续反复构建时直接复用 JSON，不再重跑向量化和章节/句子对齐。

### 3.1 保存 alignment JSON

```bash
UV_CACHE_DIR=/tmp/uv-cache \
PYTHONPATH=. \
HF_HOME=/root/projs/bookalign/.cache/huggingface \
SENTENCE_TRANSFORMERS_HOME=/root/projs/bookalign/.cache/huggingface \
TRANSFORMERS_CACHE=/root/projs/bookalign/.cache/huggingface/transformers \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run python -m bookalign.cli \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  "tests/artifacts/金阁寺-段落级回写.epub" \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode paragraph \
  --chapter-match-mode structured \
  --layout-direction horizontal \
  --alignment-json-output "tests/artifacts/金阁寺-对齐结果.json"
```

说明：

- 这条命令会同时生成 EPUB 和对齐 JSON
- JSON 中保存的是完整 `AlignmentResult`，包含 pair、segment、CFI、paragraph 锚点和句内位置信息

### 3.2 从 alignment JSON 直接 build

```bash
UV_CACHE_DIR=/tmp/uv-cache \
PYTHONPATH=. \
HF_HOME=/root/projs/bookalign/.cache/huggingface \
SENTENCE_TRANSFORMERS_HOME=/root/projs/bookalign/.cache/huggingface \
TRANSFORMERS_CACHE=/root/projs/bookalign/.cache/huggingface/transformers \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_OFFLINE=1 \
uv run python -m bookalign.cli \
  "books/金閣寺 (三島由紀夫) (Z-Library).epub" \
  "books/金阁寺 (三岛由纪夫) (Z-Library).epub" \
  "tests/artifacts/金阁寺-句子级回写-JSON构建.epub" \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode inline \
  --layout-direction horizontal \
  --alignment-json-input "tests/artifacts/金阁寺-对齐结果.json"
```

说明：

- 提供 `--alignment-json-input` 后，会跳过章节匹配和 Bertalign
- 这条路径适合集中验证 builder、样式、阅读器兼容和 XHTML 结构

## 4. 编程调用

### 4.1 正常端到端

```python
from pathlib import Path
from bookalign.pipeline import run_bilingual_epub_pipeline

alignment = run_bilingual_epub_pipeline(
    source_epub_path=Path("source.epub"),
    target_epub_path=Path("target.epub"),
    output_path=Path("out.epub"),
    source_lang="ja",
    target_lang="zh",
    builder_mode="source_layout",
    writeback_mode="inline",
    chapter_match_mode="structured",
    layout_direction="horizontal",
    alignment_json_output_path=Path("alignment.json"),
)
```

### 4.2 直接从 JSON build

```python
from pathlib import Path
from bookalign.pipeline import build_bilingual_epub_from_alignment_json

alignment = build_bilingual_epub_from_alignment_json(
    source_epub_path=Path("source.epub"),
    target_epub_path=Path("target.epub"),
    alignment_json_path=Path("alignment.json"),
    output_path=Path("rebuilt.epub"),
    builder_mode="source_layout",
    writeback_mode="inline",
    layout_direction="horizontal",
)
```

## 5. 当前推荐测试流程

对同一本真实书做 builder 调整时，推荐顺序：

1. 先跑一次完整链路，并保存 alignment JSON
2. 后续所有 builder 调整都优先用 `--alignment-json-input`
3. 只有在 extractor、章节匹配或 Bertalign 参数变化时，才重新生成 JSON

对当前样本书，推荐缓存：

- `tests/artifacts/金阁寺-对齐结果.json`
- `tests/artifacts/假面的告白-对齐结果.json`

这样后续 paragraph / inline / simple / 样式调试都可以直接复用对齐结果。
