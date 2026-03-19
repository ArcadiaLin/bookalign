# BookAlign 测试与调用说明

本文档集中说明当前项目里与抽取、对齐、builder 回归相关的常用调用方式、参数和推荐用法。

当前正式 pipeline 只有一条：

- `extract_mode='filtered_preserve'`

仓库中不再保留真实书 JSON/EPUB 基线目录。`tests/artifacts/` 仅保留：

- `tests/artifacts/batch_reader_reports/`

其他 builder 回归产物都应作为本地临时文件生成和清理。

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
  "/tmp/金阁寺-句子级回写.epub" \
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
- `--enable-local-realign`

推荐组合：

- builder 调试优先 `source_layout + inline + horizontal`
- 对齐质量调试优先 `simple`
- `--enable-local-realign` 只建议在已知问题书上显式打开

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
  "/tmp/金阁寺-段落级回写.epub" \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode paragraph \
  --layout-direction horizontal \
  --alignment-json-output "/tmp/金阁寺-对齐结果.json"
```

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
  "/tmp/金阁寺-句子级回写.epub" \
  --source-lang ja \
  --target-lang zh \
  --builder-mode source_layout \
  --writeback-mode inline \
  --layout-direction horizontal \
  --alignment-json-input "/tmp/金阁寺-对齐结果.json"
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
4. 测试完成后清理本地产物，不把真实书 JSON/EPUB 留在仓库里

## 6. 当前对齐问题检查建议

对疑似问题书，建议按顺序审查 JSON，而不是只看单个 pair：

1. 先找最近的稳定 `1-1` 区。
2. 再看后续 `8-12` 个 pair 是否突然出现：
   - 多个 `4-1/1-4`
   - 多个 `1-0/0-1`
   - 句长比极端失衡
3. 如果这些异常发生在边界之外，就很可能不是正常 paratext，而是正文断链。

当前最需要继续关注的是《假面的告白》繁中的正文中段断链，而不是额外维护更多 extract 主轴。
