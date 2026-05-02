# BookAlign

BookAlign 用来把一本外语原著 EPUB 和它的正式译本 EPUB 做结构化对齐，再重建成适合对照阅读的双语 EPUB。

它不是机翻工具。它做的是：

1. 从原著和译本里抽取正文句段。
2. 用多语 embedding + 动态规划做局部或章节级对齐。
3. 保留原书结构，把译文按段落或句子回写到原文 EPUB 里。

当前项目主要面向小说阅读场景，尤其是日语原著配中文译本，也支持英语、西语等语言对的基础流程。

## 两种运行方式

这个仓库目前同时提供两种运行方式：

1. 推荐方式：`skills/bookalign-labse`
2. 直接方式：`uv run bookalign ...` CLI pipeline

推荐优先使用 skill。

原因很直接：

- skill 走的是 review-first 流程，先检查环境、再抽取、再审查章节与正文漂移、再做局部切片对齐，最后再 build
- skill 已经把当前 production workflow 中最容易出错的环节显式化了，例如 `chapter_id` 一致性自检、`slice_plan`、未对齐段落复查
- 对脏 EPUB、前后附文混入正文、章节编号漂移、注释/评论并入正文这类真实问题，skill 比一把跑到底的 CLI 更稳

CLI pipeline 仍然保留，适合：

- 输入书籍结构比较干净
- 你已经知道章节映射大致正确
- 想快速产出一个初版 EPUB 或对齐 JSON

## 推荐运行环境

基础环境建议：

- Python `3.12`
- `uv`
- 建议优先使用项目虚拟环境或 `uv run`
- 本地 LaBSE 模型路径，或可用的 `HF_TOKEN`

对齐后端建议：

- 首选本地 CUDA + 本地 LaBSE 路径
- 没有 GPU 时可以先做抽取、检查、章节审阅；CPU 也能跑对齐，但速度会明显慢很多
- 如果不准备本地模型，可以退回 Hugging Face inference，但要显式配置 `HF_TOKEN`

显存建议：

- 经验上，`8 GB+` 显存更适合稳定跑本地 LaBSE 和章节级对齐
- `4-6 GB` 显存可以尝试较小章节或分 slice 运行，但不建议默认整书直跑
- 如果只有 CPU，建议使用 skill 的 staged workflow，而不是直接 whole-book CLI

环境自检建议：

```bash
uv run python skills/bookalign-labse/scripts/check_environment.py --json
```

这会给出：

- `recommended_backend`
- `recommended_model_name`
- `recommended_device`
- `preferred_local_model`

## 适合什么场景

- 想对照读文学原著，但不想在两个阅读器之间来回切换
- 想保留正式译本，而不是依赖机翻
- 想把对齐结果存成 JSON，后续单独调试 builder 或阅读样式
- 想先人工审查章节与正文漂移，再决定如何 build

## 安装

项目使用 Python 3.12 和 `uv`。

```bash
uv sync --group dev --group align
```

如果你本地已经有 LaBSE，建议显式传本地模型路径，而不是依赖首次在线解析。

## 推荐用法：Skill

如果你在 Codex 环境中使用这个仓库，优先使用：

- [skills/bookalign-labse/SKILL.md](skills/bookalign-labse/SKILL.md)

推荐流程是：

1. 确认 `<python-entry>`、`<skill-root>`、模型路径、是否允许远程推理、artifacts 目录
2. 运行 `check_environment.py`
3. 抽取两本书
4. 检查 `list_book_chapters`、`get_chapter_preview`、`sentence_segments`
5. 做章节一致性自检
6. 为 clean slice 制作 `slice_plan`
7. 分 slice 对齐
8. 用 `review_unaligned_segments(...)` 复查所有未对齐段落
9. 导出 review artifact，再 build 最终 EPUB

完整生产流程见：

- [skills/bookalign-labse/references/production-workflow.md](skills/bookalign-labse/references/production-workflow.md)

## 直接用法：CLI Pipeline

对于结构较干净的书，可以直接运行 CLI pipeline：

```bash
uv run bookalign \
  "books/source.epub" \
  "books/target.epub" \
  "out/output.epub" \
  --source-lang ja \
  --target-lang zh \
  --model-name /path/to/LaBSE
```

这条命令默认就是：

- `builder-mode=source_layout`
- `writeback-mode=paragraph`
- `layout-direction=horizontal`
- `device=cuda`

如果你想输出更密集的句子级交错阅读版本：

```bash
uv run bookalign \
  "books/source.epub" \
  "books/target.epub" \
  "out/output-inline.epub" \
  --source-lang ja \
  --target-lang zh \
  --model-name /path/to/LaBSE \
  --writeback-mode inline
```

如果你想先保存对齐结果 JSON，后面只调 builder：

```bash
uv run bookalign \
  "books/source.epub" \
  "books/target.epub" \
  "out/output.epub" \
  --source-lang ja \
  --target-lang zh \
  --model-name /path/to/LaBSE \
  --alignment-json-output "out/alignment.json"
```

后续可直接从 JSON 重建：

```bash
uv run bookalign \
  "books/source.epub" \
  "books/target.epub" \
  "out/output-rebuilt.epub" \
  --source-lang ja \
  --target-lang zh \
  --alignment-json-input "out/alignment.json"
```

当前 CLI pipeline 仍然是一个相对直接的 one-shot 流程：

```text
source EPUB + target EPUB
-> filtered_preserve extraction
-> heuristic chapter matching
-> Bertalign alignment
-> EPUB build
```

它适合干净输入，但不应替代 skill 的 staged review 工作流。

## 效果展示

下面这三张图分别展示《金阁寺》句子级、《金阁寺》段落级，以及《哈利波特》段落级的阅读效果。

- `docs/images/kinkaku-inline.png`
- `docs/images/kinkaku-paragraph.png`
- `docs/images/harry-potter-paragraph.png`

![《金阁寺》句子级对齐](docs/images/kinkaku-inline.png)
![《金阁寺》段落级对齐](docs/images/kinkaku-paragraph.png)
![《哈利波特》段落级对齐](docs/images/harry-potter-paragraph.png)

## 当前特性

- 保留原书 spine 顺序和大部分正文结构
- 支持 `paragraph` 和 `inline` 两种回写方式
- 保存 `AlignmentResult` 为 JSON，方便复用和调试
- 对目录、注释、前后附文等非正文做保留，不直接混入正文对齐
- 支持把目标侧未匹配章节保存在 JSON 中，并单独写入附录页
- 修复脚注引用与回跳，避免注释页成为死链接
- 中文译文段落在 build 时默认写入两个空格的段首缩进
- skill 路径支持 `slice_plan`、未对齐段落复查、review artifact 导出

## 已知限制

- 目前最稳定的组合仍然是日语小说 / 英语小说 -> 中文译本
- EPUB 本身的格式质量影响很大，脏 TOC、异常脚注、碎片化 XHTML 都会拖累效果
- CLI 的 whole-book 章节匹配仍然是启发式的，不应把它当作稳定真值
- `inline` 模式对 source EPUB 结构要求更高，不如 `paragraph` 稳
- 诗歌、公式、图注、图文混排页面目前不是重点优化对象
- 依赖 LaBSE 一类多语模型，显存、启动成本和环境准备成本都高于普通脚本工具

## 仓库结构

```text
bookalign/
├── align/      # 对齐抽象与 Bertalign 适配
├── epub/       # EPUB 读取、抽取、CFI、builder
├── models/     # Segment / AlignmentResult 等共享模型
├── cli.py      # 命令行入口
└── pipeline.py # 端到端 one-shot pipeline

skills/
└── bookalign-labse/   # 推荐使用的 review-first skill

docs/           # README 配图与补充文档
scripts/        # 环境与运行时辅助脚本
tests/          # pytest
```

## 文档

- [技术细节、当前路线与已知边界](TECHNICAL.md)
- [推荐 skill 的 production workflow](skills/bookalign-labse/references/production-workflow.md)

## Acknowledgements

这个项目直接受益于下面这些开源项目：

- [Flow](https://github.com/pacexy/flow)：README 和演示里使用的效果图就是用它渲染的
- [Vecalign](https://github.com/thompsonb/vecalign)：最早是从这个项目开始系统了解文本对齐算法路线
- [Bertalign](https://github.com/bfsujason/bertalign)：当前 BookAlign 使用的对齐后端
- [calibre](https://github.com/kovidgoyal/calibre)：提供了 EPUB CFI 相关的重要实现参考

## 开发

运行测试：

```bash
uv run pytest
```

只跑核心测试：

```bash
uv run pytest skills/bookalign-labse/tests/test_service_api.py skills/bookalign-labse/tests/test_builder_refactor.py -q
```

## 未来方向

- 继续收敛 skill-first 的 staged production workflow
- 改善更多语言对、更多 EPUB 风格下的分句和章节匹配
- 为局部错位窗口增加更稳的自动修正策略
- 给 builder 加更细的排版控制与阅读器兼容策略
- 从离线 EPUB 工具逐步走向阅读器内的对照阅读组件
