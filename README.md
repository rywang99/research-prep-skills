# Auto Research Skills

面向 Codex 的自动化调研 skills 库，用于把一个研究主题转换为可追踪的日/周/月报、近一年热词/趋势分析、研究缺口、idea 规划或实验路线图，并输出自包含中文 HTML 报告。

## 使用示例

在 Codex 中可以直接按 skill 名称调用：

```text
使用 $auto-research 调研“空间音频大模型”最近一周的研究和产业动态，生成中文 HTML 报告，并更新本地知识库。
```

```text
使用 $research-yearly-trends 分析“具身智能大模型”近一年研究趋势、机会和风险，生成中文 HTML 趋势报告。
```

```text
使用 $paper-trace 分析论文 arXiv:2606.13095 的技术脉络、实验协议和复现风险，生成中文 HTML。
```

```text
使用 $research-gap-analysis 分析“空间音频大模型”的现有不足和可验证机会，生成中文 HTML。
```

```text
使用 $research-idea-planning 基于“空间音频大模型”的缺口报告构思 5 个可发表 idea，并排序。
```

```text
使用 $experiment-roadmap 为 Cross-Format Spatial Token Alignment 规划实验验证路线，不运行实验。
```

```text
使用 $formula-derivation 为 Cross-Format Spatial Token Alignment 整理变量、假设、推导步骤和 sanity checks，不运行实验。
```

更多提示词示例见 `PROMPTS.md`。

## 能力概览

- `auto-research`：总控入口，按用户意图自动路由到合适的调研模式。
- `research-daily`：今日或最近 24 小时动态追踪，默认不生成研究热词/趋势聚类。
- `research-weekly`：最近 7 天论文、开源项目、产品和产业信号周报，默认不生成研究热词/趋势聚类。
- `research-monthly`：最近 30 天阶段性综述。
- `research-yearly-hotwords`：近一年研究热词、增长信号和代表证据分析。
- `research-yearly-trends`：近一年趋势聚类、驱动因素、机会和风险分析。
- `research-gap-analysis`：总结领域现有不足、评价瓶颈、数据缺口和可验证机会。
- `research-idea-planning`：基于调研证据生成和排序研究 idea，不运行实验。
- `experiment-roadmap`：把选定 idea 转成 claim-driven 实验路线图，不创建或提交实验任务。
- `formula-derivation`：为理论型方向整理变量、假设、推导步骤和验证条件，不声称自动证明。
- `paper-trace`：针对单篇论文生成技术溯源、重点阅读信号和复现风险 HTML。
- `scripts/collect_sources.py`：从无密钥公共 API 采集候选来源，生成可复用 JSONL。
- `scripts/trace_report_papers.py`：为日/周调研自动嵌入所有区间内文献的折叠 trace。

## 目录结构

```text
.agents/skills/auto-research/              # 调研总控 skill
.agents/skills/research-*/                 # 各调研模式的 skill 指令
.agents/skills/formula-derivation/         # 理论准备与公式推导规划 skill
.agents/skills/paper-trace/                # 单篇论文技术溯源 skill
.agents/skills/auto-research-common/       # 共享配置、模板、schema、渲染脚本
examples/                                  # 示例报告和采集结果 fixture
scripts/                                   # 仓库级校验和脚手架工具
reports/                                   # 本地生成的 HTML/JSON 报告，默认不入库
knowledge_base/                            # 本地调研知识库与轻量图谱，默认不入库
```

## 快速开始

校验 skills、配置和渲染流程：

```bash
python3 scripts/validate_skills.py
```

渲染示例报告：

```bash
python3 .agents/skills/auto-research-common/scripts/render_report.py \
  --input examples/minimal_report.json \
  --output reports/demo/demo_weekly.html \
  --update-kb
```

采集候选来源：

```bash
python3 scripts/collect_sources.py \
  --topic "automated research agent" \
  --query "automated research agent" \
  --sources arxiv,openalex,github \
  --window-days 30 \
  --limit-per-source 5 \
  --output /tmp/collected_sources.jsonl
```

采集脚本默认使用 arXiv、OpenAlex 和 GitHub Search 等无密钥来源；如设置 `GITHUB_TOKEN`，GitHub 请求限额会更高。未传 `--output` 时，结果写入 `knowledge_base/<topic_slug>/collected_sources.jsonl`。

单篇论文技术溯源：

```bash
python3 scripts/trace_single_paper.py \
  --paper "2606.13095" \
  --topic "多说话人语音识别"
```

周报/日报在渲染前自动执行论文 trace：

```bash
python3 scripts/trace_report_papers.py \
  --report reports/<topic_slug>/YYYY-MM-DD_weekly.json
```

论文 trace 会以默认 `--jobs 8` 并发执行，并嵌入 HTML 的可折叠区块；不会缓存 PDF，也不会写回 PDF 注释。

新增调研模式示例：

```bash
python3 scripts/new_research_mode.py quarterly \
  --label 季度调研 \
  --window-days 90 \
  --description "最近 90 天阶段性趋势复盘"
```

## 输出与隐私

- 默认报告路径：`reports/<topic_slug>/YYYY-MM-DD_<mode>.html`。
- 单篇论文 trace 默认路径：`reports/paper-trace/<category_slug>/<method_slug>.html`。
- 默认知识库路径：`knowledge_base/<topic_slug>/`，其中 `entities.jsonl`、`links.jsonl`、`graph_latest.json` 是 research-wiki/wiki-enrich 风格的轻量图谱增强。
- `reports/*` 和 `knowledge_base/*` 已在 `.gitignore` 中忽略，只保留 `.gitkeep` 占位文件，避免把个人调研报告、来源列表、运行记录提交到 Git。
- 不要提交 API Key、浏览器 Cookie、私有源导出或其他敏感材料。

## 开发约定

- 新模式统一注册到 `.agents/skills/auto-research-common/config/research_modes.json`。
- 候选来源采集优先通过 `scripts/collect_sources.py` 生成 JSONL，再由 Agent 复核关键来源并整理成报告 JSON。
- 报告 JSON 字段应遵循 `.agents/skills/auto-research-common/references/report_schema.md`。
- 来源引用和可信度判断遵循 `.agents/skills/auto-research-common/references/source_policy.md`。
- Python 脚本优先使用标准库，保持依赖轻量。
- 修改 schema、模板、知识库图谱或渲染行为后，更新 `examples/` fixture 并运行 `python3 scripts/validate_skills.py`。
